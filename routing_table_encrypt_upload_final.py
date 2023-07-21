import os
import psutil
import platform
import ctypes
import sys
import requests
import base64
from cryptography.fernet import Fernet
from datetime import datetime
import subprocess

# Function to restart the script with admin privileges
def restart_with_admin():
    if platform.system() != 'Windows':
        print("This script requires Windows platform.")
        return

    if ctypes.windll.shell32.IsUserAnAdmin():
        print("Already running with administrative privileges.")
        return

    script_path = sys.argv[0]
    params = ' '.join([script_path] + sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

    sys.exit(0)

# Function to encrypt data
def encrypt_data(data, encryption_key):
    if isinstance(data, bytes):
        data = data.decode()  # Decode bytes to a string
    cipher_suite = Fernet(encryption_key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

# Function to upload data to GitHub
def upload_data_to_github(data, file_path, github_repo, github_token, branch="main"):
    encoded_data = base64.b64encode(data).decode()

    url = f"https://api.github.com/repos/{github_repo}/contents/{file_path}"
    data = {
        "message": f"Upload {file_path}",
        "content": encoded_data,
        "encoding": "base64",
        "branch": branch
    }
    headers = {
        "Authorization": f"Bearer {github_token}"
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    print(f"Data {file_path} uploaded successfully.")

# Restart the script with admin privileges
restart_with_admin()

try:
    # Define the GitHub repository and personal access token
    github_repo = "ck-prime/forensics_test3"
    github_token = "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"

    # Generate encryption key
    encryption_key = Fernet.generate_key()

    # Upload encryption key to the repository
    upload_data_to_github(encryption_key, "key_routing_table.txt", github_repo, github_token, branch="main")

    # Extract and save the routing table
    system = platform.system()
    if system == "Windows":
        command = "route print"
    elif system == "Linux" or system == "Darwin":
        command = "netstat -rn"
    else:
        print("Unsupported operating system.")
        sys.exit(1)

    routing_table_output = subprocess.check_output(command, shell=True, universal_newlines=True)

    # Encrypt and upload the routing table
    encrypted_routing_table = encrypt_data(routing_table_output, encryption_key)
    upload_data_to_github(encrypted_routing_table, "routing_table.txt", github_repo, github_token, branch="main")

    # Generate and upload timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_file_content = f"Timestamp: {timestamp}\n"
    timestamp_file_content += "Routing Table: routing_table.txt\n"

    encrypted_timestamp_file_content = encrypt_data(timestamp_file_content, encryption_key)
    upload_data_to_github(encrypted_timestamp_file_content, "time_stamp_routing_table.txt", github_repo, github_token, branch="main")

    print("Routing table extraction completed.")

except Exception as e:
    print("An error occurred during routing table extraction:", str(e))

# Wait for user input before exiting
input("Press any key to exit...")
