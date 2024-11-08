import os
import re
import sys
import requests
import zipfile
import shutil
from tqdm import tqdm
import subprocess
import json

# Define the GitHub repository details
GITHUB_REPO = 'NoLaCobra504/WordlePY'  # Repository in the format "owner/repo"
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'

# Path to store the latest version information
VERSION_FILE = 'latest_version.json'

def get_latest_version_from_github():
    """Fetch the latest release version from GitHub using the GitHub API."""
    try:
        # Make a GET request to GitHub's API to fetch the latest release
        response = requests.get(GITHUB_API_URL)
        
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release['tag_name']  # The version is stored in 'tag_name'
            print(f"Latest version on GitHub: {latest_version}")
            return latest_version
        else:
            print(f"Error fetching latest release: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching latest version from GitHub: {e}")
        return None

def get_current_version_from_file():
    """Read the current version from the local `latest_version.json` file."""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as file:
            data = json.load(file)
            return data.get("version")
    return None

def update_version_file(version):
    """Update the `latest_version.json` file with the new version."""
    data = {"version": version}
    try:
        with open(VERSION_FILE, 'w') as file:
            json.dump(data, file)
        print(f"Version {version} has been saved to {VERSION_FILE}")
    except Exception as e:
        print(f"Failed to update version file: {e}")

def download_update(latest_version):
    """Download the update ZIP file."""
    try:
        # Correct URL format for GitHub releases
        zip_url = f'https://github.com/{GITHUB_REPO}/releases/download/{latest_version}/WordlePY_{latest_version}.zip'
        print(f"Downloading update from: {zip_url}")
        response = requests.get(zip_url, stream=True, allow_redirects=True)

        if response.status_code != 200:
            print(f"Failed to download the file: HTTP {response.status_code}")
            return None

        # Save the ZIP file
        zip_filename = f'WordlePY_{latest_version}.zip'
        total_size = int(response.headers.get('content-length', 0))

        with open(zip_filename, 'wb') as file, tqdm(
            desc="Downloading update",
            total=total_size,
            unit='B',
            unit_scale=True
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

        return zip_filename
    except Exception as e:
        print(f"Download failed: {e}")
        return None

def extract_update(zip_file):
    """Extract the update files from the ZIP file."""
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('update_folder')
        return 'update_folder'
    except Exception as e:
        print(f"Extraction failed: {e}")
        return None

def replace_files(update_folder):
    """Replace the old files with the updated ones, deleting only WordlePY-related files."""
    try:
        for item in os.listdir(update_folder):
            s = os.path.join(update_folder, item)
            d = os.path.join('.', item)
            
            # If it's a directory or file related to WordlePY, replace it
            if os.path.isdir(s):
                # Remove existing WordlePY directories
                if os.path.exists(d):
                    shutil.rmtree(d, ignore_errors=True)
                shutil.copytree(s, d)
            else:
                # If it's a file, copy it over (overwrite if necessary)
                shutil.copy2(s, d)
                
        return True
    except Exception as e:
        print(f"File replacement failed: {e}")
        return False

def restart_program():
    """Restart the application after updating."""
    print("Restarting the application with the updated version...")
    
    # Ensure that we spawn a new process for the updated version
    python = sys.executable
    subprocess.Popen([python] + sys.argv)  # Restart the program
    sys.exit()  # Exit the current process

def main():
    # Get the latest release version from GitHub
    latest_version = get_latest_version_from_github()
    
    if not latest_version:
        print("Failed to fetch the latest version. Exiting.")
        return

    # Get the current installed version from `latest_version.json`
    current_version = get_current_version_from_file()

    # If the current version matches the latest version, no update is needed
    if current_version == latest_version:
        print("The application is already up to date.")
        return

    print(f"Current version: {current_version} -> Latest version: {latest_version}")

    # Download the update if the versions differ
    zip_file = download_update(latest_version)
    directory_fd = os.getcwd()
    files_fd = os.listdir(directory_fd)
    version_pattern_fd = re.compile(r"^WordlePY_v(\d+)\.(\d+)\.(\d+)\.py$")
    latest_version_fd = None
    
    for file in files_fd:
        match = version_pattern_fd.match(file)
    if match:
        if not latest_version_fd or file > latest_version_fd:
            latest_version_fd = file
    
    for file in files_fd:
        if file != latest_version_fd and (version_pattern_fd.match(file) or file == "WordlePY.py"):
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Failed to delete {file}: {e}")
    if latest_version_fd:
        print(f"Kept the latest version: {latest_version_fd}")
    else:
        print("No versioned files found.")
    
    
    if zip_file:
        update_folder = extract_update(zip_file)
        
        if update_folder:
            if replace_files(update_folder):
                print("Update successful. Restarting the application...")
                os.remove(zip_file)  # Clean up the downloaded ZIP file
                shutil.rmtree(update_folder)  # Clean up the extracted folder
                update_version_file(latest_version)  # Save the new version to the version file
                restart_program()  # Restart the program to run the updated version
            else:
                print("Failed to replace files.")
        else:
            print("Failed to extract update files.")
    else:
        print("Failed to download update.")

if __name__ == "__main__":
    main()
