"""
This module contains the code to create a linkFroge link for the local server.
It uses the linkFroge API to create a link and returns the link to the user.
It also checks if ngrok is installed and downloads it if necessary.
"""

import io
from operator import ne
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
    "linkfroge_api": "https://127.0.0.1:5000/api",
    "localng-api": "http://127.0.0.1:4040/api/tunnels",
    "service-id": None,
    "service-token": None,
    "thrade_flage": False,
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
                ngrok_path.chmod(0o755)
            except Exception:
                pass

        print("[+] Ngrok downloaded and extracted successfully.")

        subprocess.run('chmod +x ' + str(ngrok_path), shell=True, check=True)

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
        print("[+] Ngrok auth token not found.")
        return False

    # Check if the ngrok auth token is valid by making a request to the local ngrok API
    try:
        response = requests.get(config['localng-api'])
        if response.status_code == 200:
            print("[+] Ngrok auth token is valid.")
            return True
        else:
            print("[+] Ngrok auth token is invalid.")
            promppt_auth_token = input("[+] Please enter your ngrok auth token: ")
            try:
                subprocess.run(
                    [
                        str(ngpath / ngrok_executable),
                        "add-authtoken", promppt_auth_token,
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



if __name__ == "__main__":
    if not does_ngrok_exist():
        DownloadNgrok(config["download-ngrok"], config["ngpath"])