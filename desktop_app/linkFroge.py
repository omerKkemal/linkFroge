"""
This module contains the code to create a linkFroge link for the local server.
It uses the linkFroge API to create a link and returns the link to the user.
It also checks if ngrok is installed and downloads it if necessary.
"""

import io
from operator import ne
import os
import os
import zipfile
from pathlib import Path
import argparse
import subprocess

import requests
from tqdm import tqdm


# Directory where ngrok will be stored
ngpath = Path.home() / ".linkfroge"

# ngrok executable name
ngrok_executable = "ngrok.exe" if __import__("platform").system() == "Windows" else "ngrok"


def get_platform():
    """Determine the platform for downloading ngrok."""
    plat = __import__("platform").system()
    if plat == "Windows":
        return "windows-amd64"
    elif plat == "Linux":
        return "linux-amd64"
    elif plat == "Darwin":
        return "darwin-amd64"
    else:
        raise Exception("Unsupported platform")

plat = get_platform()


config = {
    "ngpath": str(ngpath),
    "verbose": False,
    "port": 55555,
    "linkfroge_api": "http://127.0.0.1:5000/api",
    "localng-api": "http://127.0.0.1:4040/api/tunnels",
    "service-id": None,
    "service-token": None,
    "config_file": str(ngpath / "ngrok.yml"),
    "ng-auth-token": any(ngpath.glob("*.yml")),
    "download-ngrok": f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-{plat}.zip",
}


onStartInfo = {
    "service_id": None,
    "service_token": None,
    "service_link": None,
    "args": {}
}


def does_ngrok_exist():
    """Create the directory if needed and check whether ngrok exists."""
    ngpath.mkdir(parents=True, exist_ok=True)

    ngrok_path = ngpath / ngrok_executable

    if ngrok_path.is_file():
        print(f"[+] Ngrok already exists: {ngrok_path}")
        return True

    print("[!] Ngrok not found.")
    return False


def DownloadNgrok(url, path):
    try:
        print("[+] Downloading ngrok...")

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = io.BytesIO()

        with tqdm(
            total=total_size,
            desc="Downloading",
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded.write(chunk)
                    progress.update(len(chunk))

        print("[+] Extracting ngrok...")

        downloaded.seek(0)

        with zipfile.ZipFile(downloaded) as zip_ref:
            zip_ref.extractall(path)

        # Make executable on Linux/macOS
        ngrok_path = Path(path) / ngrok_executable
        if ngrok_path.exists():
            try:
                subprocess.run('chmod +x ' + str(ngrok_path), shell=True, check=True)
                ngrok_path.chmod(0o755)
            except Exception:
                pass

        print("[+] Ngrok downloaded and extracted successfully.")

    except requests.RequestException as e:
        print(f"[!] Download failed: {e}")
    except zipfile.BadZipFile:
        print("[!] Downloaded file is not a valid ZIP archive.")
    except Exception as e:
        print(f"[!] An error occurred: {e}")


def check_if_service_id_exists():
    """Check if the service ID exists in the config."""
    header = {
        "Authorization": f"Bearer {config['service-token']}",
        "Service-Link-Id": f"{config['service-id']}",
    }
    link = requests.get(f"{config['linkfroge_api']}/get_link", headers=header)

    if link.status_code == 200:
        print("[+] Service ID exists.")
        return True, link.json()['link']

    print("[!] Service ID does not exist.")
    return False, None



def update_service_link(new_link):
    """Update the service link in the config."""
    header = {
        "Authorization": f"Bearer {config['service-token']}",
    }
    body = {
        "Service-Link-Id": f"{config['service-id']}",
        "link": new_link,
    }

    response = requests.post(
        f"{config['linkfroge_api']}/update_link",
        headers=header,
        json=body
    )
    if response.status_code == 200:
        print("[+] Service link updated successfully.")
        return True

    print("[!] Failed to update service link.")
    return False


def is_ng_auth_token_valid():
    """Check if the ngrok auth token is valid."""
    if not config['ng-auth-token']:
        print("[!] Ngrok auth token not found.")
        return False

    # Check if the ngrok auth token is valid by making a request to the local ngrok API
    try:
        auth_file_exists = str(ngpath / "ngrok.yml")
        if os.path.exists(auth_file_exists):
            print("[+] Ngrok auth token is valid.")
            return True
        else:
            print("[!] Ngrok auth token is invalid.")
            prompt_auth_token = input("[+] Please enter your ngrok auth token: ")
            try:
                subprocess.run(
                    [
                        str(ngpath / ngrok_executable),
                        "add-authtoken", prompt_auth_token,
                        "--config", str(ngpath / "ngrok.yml")
                    ],
                    check=True
                )
                return True
            except Exception as e:
                print(f"[!] Failed to add ngrok auth token: {e}")
                return False
    except requests.RequestException:
        print("[!] Failed to connect to the local ngrok API.")
        return False


def start_ngrok(port):
    """Start ngrok on the specified port."""
    try:
        subprocess.Popen(
            [
                str(ngpath / ngrok_executable), 
                "http", str(port),
                "--config", str(ngpath / "ngrok.yml")
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[+] Ngrok started on port {port}.")
    except Exception as e:
        print(f"[!] Failed to start ngrok: {e}")


def stop_ngrok():
    """Stop ngrok by terminating the process."""
    try:
        if __import__("platform").system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", ngrok_executable], check=True)
        else:
            subprocess.run(["pkill", "-f", ngrok_executable], check=True)
        print("[+] Ngrok stopped.")
    except Exception as e:
        print(f"[!] Failed to stop ngrok: {e}")


def get_ngrok_link():
    """Get the public link from the local ngrok API."""
    try:
        response = requests.get(config['localng-api'])
        if response.status_code == 200:
            tunnels = response.json().get("tunnels", [])
            if tunnels:
                public_url = tunnels[0].get("public_url")
                print(f"[+] Ngrok public URL: {public_url}")
                return True, public_url
            else:
                print("[!] No tunnels found.")
                return False, None
        else:
            print("[!] Failed to get ngrok tunnels.")
            return False, None
    except requests.RequestException as e:
        print(f"[!] Error connecting to local ngrok API: {e}")
        return False, None

def main():
    import time
    import sys

    parser = argparse.ArgumentParser(description="LinkFroge - Create a link for your local server using ngrok.")
    parser.add_argument("--port", type=int, default=55555, help="Port to expose via ngrok")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--service-id", type=str, help="Service ID for LinkFroge")
    parser.add_argument("--service-token", type=str, help="Service token for LinkFroge")
    parser.add_argument("--download-ngrok", type=str, default=config["download-ngrok"], help="URL to download ngrok if not present")
    parser.add_argument("--ngrok-auth-token", type=str, help="Ngrok auth token to authenticate with ngrok")
    parser.add_argument("--linkfroge-api", type=str, default=config["linkfroge_api"], help="LinkFroge API endpoint")

    args = parser.parse_args()

    # Update config with command‑line arguments
    config["port"] = args.port
    config["verbose"] = args.verbose
    if args.service_id:
        config["service-id"] = args.service_id
    if args.service_token:
        config["service-token"] = args.service_token
    if args.download_ngrok:
        config["download-ngrok"] = args.download_ngrok
    if args.ngrok_auth_token:
        config["ng-auth-token"] = args.ngrok_auth_token
    if args.linkfroge_api:
        config["linkfroge_api"] = args.linkfroge_api

    # If the LinkFroge API is on localhost with HTTPS, switch to HTTP (local dev servers usually don't have SSL)
    url = config["linkfroge_api"]
    if url.startswith("https://127.0.0.1") or url.startswith("https://localhost"):
        config["linkfroge_api"] = url.replace("https://", "http://")
        if config["verbose"]:
            print("[*] Changed LinkFroge API to HTTP for localhost.")

    # Store info for later use
    onStartInfo["service_id"] = config["service-id"]
    onStartInfo["service_token"] = config["service-token"]
    onStartInfo["args"] = vars(args)

    # 1. Ensure ngrok is present
    if not does_ngrok_exist():
        DownloadNgrok(config["download-ngrok"], config["ngpath"])

    # 2. Ensure ngrok auth token is set (prompts if missing)
    if not is_ng_auth_token_valid():
        print("[!] Ngrok authentication failed. Exiting.")
        return

    # 3. Start ngrok on the specified port
    print(f"[+] Starting ngrok on port {config['port']}...")
    start_ngrok(config["port"])

    # 4. Wait for ngrok to be ready and retrieve the public URL
    public_url = None
    max_retries = 12
    retry_delay = 1.5  # seconds

    for attempt in range(max_retries):
        time.sleep(retry_delay)
        success, url = get_ngrok_link()
        if success and url:
            public_url = url
            break
        if config["verbose"]:
            print(f"[*] Attempt {attempt + 1}/{max_retries} - ngrok not ready yet, retrying...")

    if not public_url:
        print("[!] Failed to obtain ngrok public URL after multiple attempts.")
        stop_ngrok()
        return

    # 5. Update or display LinkFroge service link
    service_id = config.get("service-id")
    service_token = config.get("service-token")

    if service_id and service_token:
        exists, current_link = check_if_service_id_exists()
        if exists:
            # Direct update because the helper `update_service_link` sends Service‑Link‑Id in the body,
            # but the Flask endpoint expects it in the headers.
            headers = {
                "Authorization": f"Bearer {service_token}",
                "Service-Link-Id": service_id,
            }
            body = {"link": public_url}
            try:
                response = requests.post(
                    f"{config['linkfroge_api']}/update_link",
                    headers=headers,
                    json=body
                )
                if response.status_code == 200:
                    print(f"[+] Service link updated to: {public_url}")
                else:
                    print(f"[!] Failed to update service link. Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                print(f"[!] Error updating service link: {e}")
        else:
            print("[!] Service ID does not exist. Please create the service first via the LinkFroge API.")
            print(f"    Then update the link manually with: {public_url}")
    else:
        # No credentials – just print the link
        print("[+] Ngrok tunnel is running. Public URL:", public_url)
        print("[!] To link this tunnel with a LinkFroge service, provide --service-id and --service-token.")

    # Store the link for later reference
    onStartInfo["service_link"] = public_url

    # 6. Keep the script alive until interrupted
    print("\n[+] Ngrok tunnel is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopping ngrok...")
        stop_ngrok()
        print("[+] Done.")

if __name__ == "__main__":
    main()
