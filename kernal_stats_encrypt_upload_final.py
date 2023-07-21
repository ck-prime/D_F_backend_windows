import os
import psutil
import platform
import ctypes
import sys
import requests
import base64
from cryptography.fernet import Fernet
from datetime import datetime

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

def encrypt_data(data, encryption_key):
    cipher_suite = Fernet(encryption_key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

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

# Specify the GitHub repository and personal access token
github_repo = "ck-prime/forensics_test4"
github_token = "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"

# Restart the script with admin privileges
restart_with_admin()

try:
    # Define the output directory relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(script_dir, "kernal_stats")

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Generate encryption key
    encryption_key = Fernet.generate_key()

    # Upload encryption key to the repository
    upload_data_to_github(encryption_key, "key_kernal_stats.txt", github_repo, github_token, branch="main")

    # Define the encryption key
    encryption_key = encryption_key

    # Extract and encrypt process and thread information
    process_thread_info = ""
    for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time', 'status', 'ppid']):
        process_thread_info += f"Process ID (PID): {proc.info['pid']}\n"
        process_thread_info += f"Thread ID (TID): {proc.info['pid']}\n"
        process_thread_info += f"Start Time: {proc.info['create_time']}\n"
        process_thread_info += f"End Time: {psutil.Process(proc.info['pid']).status()}\n"
        process_thread_info += f"Parent Process ID (PPID): {proc.info['ppid']}\n"
        process_thread_info += f"Status: {proc.info['status']}\n"
        process_thread_info += "\n"

    encrypted_process_thread_info = encrypt_data(process_thread_info, encryption_key)
    upload_data_to_github(encrypted_process_thread_info, "p_n_t_info.txt", github_repo, github_token, branch="main")

    # Extract and encrypt network connections
    network_connections = ""
    for conn in psutil.net_connections():
        if conn.laddr and conn.raddr:
            network_connections += f"Source IP: {conn.laddr.ip}\n"
            network_connections += f"Destination IP: {conn.raddr.ip}\n"
            network_connections += f"Local Port: {conn.laddr.port}\n"
            network_connections += f"Remote Port: {conn.raddr.port}\n"
            network_connections += f"Protocol: {conn.type}\n"
            network_connections += f"Status: {conn.status}\n"
            network_connections += "\n"

    encrypted_network_connections = encrypt_data(network_connections, encryption_key)
    upload_data_to_github(encrypted_network_connections, "net_conc.txt", github_repo, github_token, branch="main")

    # Extract and encrypt file system metadata
    file_system_metadata = ""
    for partition in psutil.disk_partitions():
        file_system_metadata += f"Device: {partition.device}\n"
        file_system_metadata += f"Mount Point: {partition.mountpoint}\n"
        file_system_metadata += f"File System Type: {partition.fstype}\n"
        file_system_metadata += f"Options: {partition.opts}\n"
        file_system_metadata += "\n"
        
        for entry in os.scandir(partition.mountpoint):
            file_system_metadata += f"Name: {entry.name}\n"
            file_system_metadata += f"Creation Time: {os.path.getctime(entry.path)}\n"
            file_system_metadata += f"Modification Time: {os.path.getmtime(entry.path)}\n"
            file_system_metadata += f"Attributes: {entry.stat().st_file_attributes}\n"
            file_system_metadata += f"Owner: {entry.stat().st_uid}\n"
            file_system_metadata += f"Access Permission: {entry.stat().st_mode}\n"
            file_system_metadata += "\n"

    encrypted_file_system_metadata = encrypt_data(file_system_metadata, encryption_key)
    upload_data_to_github(encrypted_file_system_metadata, "f_s_metadata.txt", github_repo, github_token, branch="main")

    # Extract and encrypt memory usage
    memory_usage = ""
    mem_info = psutil.Process().memory_info()
    memory_usage += f"Memory Allocation: {mem_info.rss}\n"
    memory_usage += f"Memory Deallocation: {mem_info.vms - mem_info.rss}\n"
    memory_usage += "\n"
    for map_entry in psutil.Process().memory_maps(grouped=True):
        memory_usage += f"Path: {map_entry.path}\n"
        memory_usage += f"Size: {map_entry.rss}\n"
        memory_usage += "\n"

    encrypted_memory_usage = encrypt_data(memory_usage, encryption_key)
    upload_data_to_github(encrypted_memory_usage, "mem_usage.txt", github_repo, github_token, branch="main")

    # Generate timestamp for all the files
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_file_content = f"Timestamp: {timestamp}\n"
    timestamp_file_content += f"Process and Thread Information: p_n_t_info.txt\n"
    timestamp_file_content += f"Network Connections: net_conc.txt\n"
    timestamp_file_content += f"File System Metadata: f_s_metadata.txt\n"
    timestamp_file_content += f"Memory Usage: mem_usage.txt\n"

    # Upload timestamp file to the repository
    upload_data_to_github(timestamp_file_content.encode(), "time_stamp_kernal_stats.txt", github_repo, github_token, branch="main")

    print("Kernel statistics extraction completed.")

except Exception as e:
    print("An error occurred during kernel statistics extraction:", str(e))

# Wait for user input before exiting
if platform.system() == "Windows":
    import msvcrt
    print("Press any key to exit...")
    msvcrt.getch()
else:
    input("Press Enter to exit...")
