import os
import requests
import zipfile
import shutil
import sys  # Import sys to handle program restart
from tqdm import tqdm
import subprocess

# Define the GitHub repository details
GITHUB_REPO = 'https://github.com/NoLaCobra504/WordlePY/releases/download/'

def check_for_update():
    """Check if a new update is available."""
    try:
        # Fetch the latest version from the repository
        response = requests.get('https://raw.githubusercontent.com/NoLaCobra504/WordlePY/main/latest_version.json')
        latest_version = response.json().get('version')
        
        # Compare the version from GitHub with the current state (assume we're always outdated)
        print(f"Latest version on GitHub: {latest_version}")
        
        # You can use a hardcoded check or perform other checks here
        # Here, we assume the app is always outdated (no `current_version.txt`)
        return latest_version
    except Exception as e:
        print(f"Update check failed: {e}")
        return None

def download_update(latest_version):
    """Download the update ZIP file."""
    try:
        # Correct URL format for GitHub releases
        zip_url = f'{GITHUB_REPO}v{latest_version}/WordlePY_{latest_version}.zip'
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
    """Replace the old files with the updated ones."""
    try:
        # Replace all files from the update folder to the current directory
        for item in os.listdir(update_folder):
            s = os.path.join(update_folder, item)
            d = os.path.join('.', item)
            if os.path.isdir(s):
                shutil.rmtree(d, ignore_errors=True)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        return True
    except Exception as e:
        print(f"File replacement failed: {e}")
        return False

def delete_old_files(update_folder):
    """Remove the old files (previous version) after the update is done."""
    try:
        # Get the list of files that were replaced by the update
        update_files = set(os.listdir(update_folder))  # Files in the update folder

        # Loop through the current directory and delete files/folders that were replaced
        for item in os.listdir('.'):
            if item not in update_files and item != 'update_folder' and item != f'WordlePY_{get_current_version()}.zip':
                item_path = os.path.join('.', item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)  # Delete old directories
                else:
                    os.remove(item_path)  # Delete old files
        print("Old files removed successfully.")
        return True
    except Exception as e:
        print(f"Error while removing old files: {e}")
        return False

def get_current_version():
    """Get the current version of the app (from a file or hardcoded)."""
    # This can be a hardcoded version or you can read from a version file (e.g., current_version.txt)
    return "1.0.0"  # Change this to the actual version if you have it saved elsewhere

def restart_program():
    """Restart the application after updating."""
    print("Restarting the application with the updated version...")
    python = sys.executable
    subprocess.Popen([python] + sys.argv)  # Restart the program
    sys.exit()  # Exit the current process

def main():
    # Check if the current version is up-to-date
    latest_version = check_for_update()
    
    if latest_version:
        zip_file = download_update(latest_version)
        
        if zip_file:
            update_folder = extract_update(zip_file)
            
            if update_folder:
                if replace_files(update_folder):
                    # Remove old files once the update is successful
                    if delete_old_files(update_folder):
                        print("Update successful. Restarting the application...")
                        os.remove(zip_file)  # Clean up the downloaded ZIP file
                        shutil.rmtree(update_folder)  # Clean up the extracted folder
                        restart_program()  # Restart the program to run the updated version
                    else:
                        print("Failed to remove old files.")
                else:
                    print("Failed to replace files.")
            else:
                print("Failed to extract update files.")
        else:
            print("Failed to download update.")
    else:
        print("The application is up to date.")

if __name__ == "__main__":
    main()
