import os
import platform
import psutil
import wmi
import ctypes
import requests
import base64
import sys
from cryptography.fernet import Fernet
from datetime import datetime

# Function to restart the script with admin privileges
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

# Function to encrypt data using the provided key
def encrypt_data(data, encryption_key):
    cipher_suite = Fernet(encryption_key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

# Function to upload data to a GitHub repository
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

# Function to identify all the available drives on the system
def identify_drives():
    drives = psutil.disk_partitions(all=True)
    drive_list = []
    for drive in drives:
        drive_list.append(drive.device)
    return drive_list

# Function to retrieve specifications of a drive using WMI
def document_drive_specifications(drive):
    wmi_obj = wmi.WMI()
    drive_info = wmi_obj.query("SELECT * FROM Win32_LogicalDisk WHERE DeviceID = '{}'".format(drive.rstrip('\\')))[0]
    print("Drive make: {}".format(drive_info.Caption))
    print("Drive capacity: {} GB".format(int(drive_info.Size) / (1024**3)))
    print("Drive model: {}".format(drive_info.Description))
    if hasattr(drive_info, 'InterfaceType'):
        print("Drive interface type: {}".format(drive_info.InterfaceType))
    else:
        print("Drive interface type: Unknown")

# Function to set up a write-blocker for a drive (Replace with your implementation)
def setup_write_blocker(drive):
    print("Setting up write-blocker...")

# Restart the script with admin privileges
restart_with_admin()

# Specify the GitHub repository and personal access token
github_repo = "ck-prime/forensics_test5"
github_token = "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"

# Generate encryption key
encryption_key = Fernet.generate_key()

try:
    # Upload encryption key to the repository
    upload_data_to_github(encryption_key, "key_all_list.txt", github_repo, github_token, branch="main")

    # Define the encryption key
    encryption_key = encryption_key

    # Identify all the available drives on the system
    drive_list = identify_drives()

    # Process each drive and upload encrypted data to GitHub
    for drive in drive_list:
        document_drive_specifications(drive)
        setup_write_blocker(drive)

        # Step 3: Retrieve the partition list
        partitions = psutil.disk_partitions(all=True)
        print("\nPartition List:")
        for partition in partitions:
            print("Device: {}".format(partition.device))
            print("Mountpoint: {}".format(partition.mountpoint))
            print("File System: {}".format(partition.fstype))
            print()

        # Step 4: Create a file with the list of all directories and files
        all_files_content = ""
        for root, dirs, files in os.walk(drive):
            all_files_content += f"Directory: {root}\n"
            for file_name in files:
                try:
                    all_files_content += f"File: {os.path.join(root, file_name)}\n"
                except UnicodeEncodeError:
                    pass

        # Print the output before encryption
        print(f"\nOutput for Drive {drive}:")
        print(all_files_content)

        # Encrypt the all_files_content and upload it to GitHub
        encrypted_all_files_content = encrypt_data(all_files_content, encryption_key)
        upload_data_to_github(encrypted_all_files_content, f"all_files_{drive.replace(':', '')}.txt", github_repo, github_token, branch="main")

    # Generate and upload timestamp for the entire process
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_file_content = f"Timestamp: {timestamp}\n"
    for drive in drive_list:
        timestamp_file_content += f"Drive: {drive}\n"
        timestamp_file_content += f"File: all_files_{drive.replace(':', '')}.txt\n"
    upload_data_to_github(timestamp_file_content, "time_stamp_all_list.txt", github_repo, github_token, branch="main")

    print("\nData extraction and upload completed.")

except Exception as e:
    print("An error occurred:", str(e))

# Wait for user input before exiting
input("Press any key to exit...")
