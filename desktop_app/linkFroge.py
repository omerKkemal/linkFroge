import subprocess
import requests
import time
import os
import platform
import zipfile
import argparse
import sys

# ================= DEFAULT CONFIG =================

DEFAULT_CONFIG = {
    "port": 5000,
    "backend": "https://yourdomain.com/api/service/update",
    "service_id": "abc123",
    "token": "your_secure_token",
    "install_dir": os.path.join(os.path.expanduser("~"), ".linkforge"),
    "no_download": False,
    "verbose": True
}

CHECK_INTERVAL = 5
HEARTBEAT_INTERVAL = 20
MAX_BACKOFF = 30
NGROK_API = "http://127.0.0.1:4040/api/tunnels"

# =================================================


# -----------------------------
# CLI PARSER
# -----------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="LinkForge Agent")

    parser.add_argument("--port", type=int, help="Local port to expose")
    parser.add_argument("--backend", help="Backend API URL")
    parser.add_argument("--service-id", help="Service ID")
    parser.add_argument("--token", help="Service token")
    parser.add_argument("--install-dir", help="Custom install directory")
    parser.add_argument("--no-download", action="store_true", help="Disable ngrok auto-download")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logs")

    return vars(parser.parse_args())


def merge_config(cli_args):
    config = DEFAULT_CONFIG.copy()
    for k, v in cli_args.items():
        if v is not None:
            config[k] = v
    return config


# -----------------------------
# LOGGING
# -----------------------------
def log(msg, config):
    if config["verbose"]:
        print(msg)


# -----------------------------
# PLATFORM
# -----------------------------
def get_platform():
    system = platform.system().lower()
    if "linux" in system:
        return "linux-amd64"
    elif "darwin" in system:
        return "darwin-amd64"
    elif "windows" in system:
        return "windows-amd64"
    else:
        raise Exception("Unsupported OS")


def get_ngrok_binary_path(config):
    binary = "ngrok.exe" if os.name == "nt" else "ngrok"
    return os.path.join(config["install_dir"], binary)


# -----------------------------
# DOWNLOAD NGROK
# -----------------------------
def get_ngrok_url():
    plat = get_platform()
    return f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-{plat}.zip"


def download_file(url, output_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)


def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def make_executable(path):
    if os.name != "nt":
        os.chmod(path, 0o755)


def ensure_ngrok(config):
    os.makedirs(config["install_dir"], exist_ok=True)
    binary_path = get_ngrok_binary_path(config)

    if os.path.exists(binary_path):
        log("[*] ngrok exists", config)
        return binary_path

    if config["no_download"]:
        print("[ERROR] ngrok not found and download disabled")
        sys.exit(1)

    url = get_ngrok_url()
    zip_path = os.path.join(config["install_dir"], "ngrok.zip")

    print("[*] Downloading ngrok...")
    download_file(url, zip_path)
    extract_zip(zip_path, config["install_dir"])
    make_executable(binary_path)
    os.remove(zip_path)

    print("[+] ngrok ready")
    return binary_path


# -----------------------------
# PROCESS
# -----------------------------
def start_ngrok(path, port, config):
    log("[*] Starting ngrok", config)
    return subprocess.Popen(
        [path, "http", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def stop_ngrok(proc):
    if not proc:
        return None
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except:
        proc.kill()
    return None


def is_running(proc):
    return proc and proc.poll() is None


# -----------------------------
# NGROK API
# -----------------------------
def fetch_tunnel_url():
    try:
        res = requests.get(NGROK_API, timeout=3)
        for t in res.json().get("tunnels", []):
            if t.get("proto") == "https":
                return t.get("public_url")
    except:
        return None
    return None


# -----------------------------
# BACKEND
# -----------------------------
def send_update(url, config, status="online"):
    payload = {
        "service_id": config["service_id"],
        "url": url,
        "status": status
    }

    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json"
    }

    try:
        requests.post(config["backend"], json=payload, headers=headers, timeout=5)
        log(f"[SYNC] {url}", config)
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")


# -----------------------------
# HELPERS
# -----------------------------
def detect_change(old, new):
    return new and new != old


def compute_backoff(current, success):
    return 1 if success else min(current * 2, MAX_BACKOFF)


# -----------------------------
# CORE STEP
# -----------------------------
def step(state, config, ngrok_path):
    proc = state["proc"]
    url = state["url"]
    backoff = state["backoff"]
    last_heartbeat = state["last_heartbeat"]

    if not is_running(proc):
        print("[!] ngrok stopped")
        time.sleep(backoff)
        proc = start_ngrok(ngrok_path, config["port"], config)
        return {**state, "proc": proc, "backoff": compute_backoff(backoff, False)}

    new_url = fetch_tunnel_url()

    if not new_url:
        print("[!] No tunnel URL")
        proc = stop_ngrok(proc)
        time.sleep(backoff)
        proc = start_ngrok(ngrok_path, config["port"], config)
        return {**state, "proc": proc, "backoff": compute_backoff(backoff, False)}

    if detect_change(url, new_url):
        send_update(new_url, config)
        url = new_url
        backoff = compute_backoff(backoff, True)

    now = time.time()
    if now - last_heartbeat > HEARTBEAT_INTERVAL and url:
        send_update(url, config)
        last_heartbeat = now

    return {
        "proc": proc,
        "url": url,
        "backoff": backoff,
        "last_heartbeat": last_heartbeat
    }


# -----------------------------
# MAIN
# -----------------------------
def run():
    cli_args = parse_args()
    config = merge_config(cli_args)

    ngrok_path = ensure_ngrok(config)
    proc = start_ngrok(ngrok_path, config["port"], config)

    state = {
        "proc": proc,
        "url": None,
        "backoff": 1,
        "last_heartbeat": time.time()
    }

    while True:
        try:
            state = step(state, config, ngrok_path)
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[!] Shutdown")
            stop_ngrok(state["proc"])
            break

        except Exception as e:
            print(f"[FATAL] {e}")
            state["proc"] = stop_ngrok(state["proc"])
            time.sleep(state["backoff"])
            state["proc"] = start_ngrok(ngrok_path, config["port"], config)


if __name__ == "__main__":
    run()
