import platform
import ctypes
import subprocess
import sys
import requests
import base64
from cryptography.fernet import Fernet
from datetime import datetime


def restart_with_admin():
    if platform.system() != 'Windows':
        print("This script requires Windows platform.")
        sys.exit(1)

    if ctypes.windll.shell32.IsUserAnAdmin():
        print("Already running with administrative privileges.")
        return

    script_path = sys.argv[0]
    params = ' '.join([script_path] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

    sys.exit(0)


# Restart the script with admin privileges
restart_with_admin()


def extract_arp_cache(github_repo, github_token):
    try:
        # Run the arp command to get the ARP cache
        arp_output = subprocess.check_output(['arp', '-a']).decode()

        # Generate encryption key and save it to a file
        encryption_key = Fernet.generate_key()
        key_content = base64.b64encode(encryption_key).decode()
        
        # Upload key.txt to GitHub
        url_key = f"https://api.github.com/repos/{github_repo}/contents/key_arp.txt"
        data_key = {
            "message": "Upload encryption key",
            "content": key_content,
            "encoding": "base64"
        }
        headers_key = {
            "Authorization": f"Bearer {github_token}"
        }
        response_key = requests.put(url_key, headers=headers_key, json=data_key)
        response_key.raise_for_status()

        print("Encryption key uploaded successfully.")

        # Encrypt the ARP cache
        cipher_suite = Fernet(encryption_key)
        encrypted_data = cipher_suite.encrypt(arp_output.encode())

        # Upload encrypted ARP cache to GitHub
        url_arp = f"https://api.github.com/repos/{github_repo}/contents/arp_cache.txt"
        data_arp = {
            "message": "Upload encrypted ARP cache",
            "content": base64.b64encode(encrypted_data).decode(),
            "encoding": "base64"
        }
        response_arp = requests.put(url_arp, headers=headers_key, json=data_arp)
        response_arp.raise_for_status()

        print("ARP cache uploaded successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while extracting ARP cache: {e}")
        input("Press any key to exit...")
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press any key to exit...")
        sys.exit(1)


# GitHub repository and personal access token
github_repo = "ck-prime/forensics_test1"
github_token = "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"

# Extract and upload the encrypted ARP cache and encryption key to GitHub
extract_arp_cache(github_repo, github_token)

# Create a timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timestamp_content = f"Extraction Timestamp: {timestamp}"

# Create the timestamp file
url_timestamp = f"https://api.github.com/repos/{github_repo}/contents/time_stamp_arp.txt"
data_timestamp = {
    "message": "Upload timestamp file",
    "content": base64.b64encode(timestamp_content.encode()).decode(),
    "encoding": "base64"
}
headers_timestamp = {
    "Authorization": f"Bearer {github_token}"
}
response_timestamp = requests.put(url_timestamp, headers=headers_timestamp, json=data_timestamp)
response_timestamp.raise_for_status()

if response_timestamp.status_code == 201:
    print("Timestamp file uploaded successfully.")
else:
    print("Error uploading timestamp file:", response_timestamp.text)

# Prompt user to press any key before exiting
input("Press any key to exit...")
