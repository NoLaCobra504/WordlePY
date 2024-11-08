import os
import requests
import zipfile
import shutil
from tqdm import tqdm

# Define the GitHub repository details
GITHUB_REPO = 'https://raw.githubusercontent.com/NoLaCobra504/WordlePY/main/'

CURRENT_VERSION = "1.0.0"  # This should match the version in wordle_game.py

def check_for_update():
    try:
        # Fetch the latest version information from the repository
        response = requests.get(GITHUB_REPO + 'latest_version.json')
        print("Response JSON:", response.text)  # Debugging line to check the fetched JSON
        latest_version = response.json().get('version')
        
        if latest_version > CURRENT_VERSION:
            print(f"New version {latest_version} is available.")  # Debugging line to confirm version comparison
            return latest_version
        return None
    except Exception as e:
        print(f"Update check failed: {e}")
        return None

def download_update(latest_version):
    try:
        # Correct URL format for GitHub raw files
        zip_url = f'https://github.com/NoLaCobra504/WordlePY/raw/main/updates/WordlePY_{latest_version}.zip'
        print(f"Downloading update from: {zip_url}")  # Debugging line to check URL
        response = requests.get(zip_url, stream=True, allow_redirects=True)
        
        # Check if download was successful
        if response.status_code != 200:
            print(f"Failed to download the file: HTTP {response.status_code}")
            return None
        
        # Save the ZIP file
        zip_filename = f'WordlePY_{latest_version}.zip'
        total_size = int(response.headers.get('content-length', 0))
        
        # Download the file with progress bar
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
    try:
        print(f"Extracting {zip_file}...")  # Debugging line to check extraction
        # Extract the ZIP file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('update_folder')
        return 'update_folder'
    except Exception as e:
        print(f"Extraction failed: {e}")
        return None

def replace_files(update_folder):
    try:
        # Replace old files with the new ones from the extracted folder
        for item in os.listdir(update_folder):
            s = os.path.join(update_folder, item)
            d = os.path.join('.', item)
            
            print(f"Replacing {s} with {d}")  # Debugging line to check file paths
            
            if os.path.isdir(s):
                shutil.rmtree(d, ignore_errors=True)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        return True
    except Exception as e:
        print(f"File replacement failed: {e}")
        return False

def main():
    # Check for the latest version from the GitHub repository
    latest_version = check_for_update()
    
    if latest_version:
        # Download and update if a new version is available
        zip_file = download_update(latest_version)
        
        if zip_file:
            # Extract and replace the files
            update_folder = extract_update(zip_file)
            
            if update_folder:
                if replace_files(update_folder):
                    print("Update successful. Please restart the application.")
                    os.remove(zip_file)  # Clean up the downloaded ZIP file
                    shutil.rmtree(update_folder)  # Clean up the extracted folder
                else:
                    print("Failed to replace files.")
            else:
                print("Failed to extract update files.")
        else:
            print("Failed to download update.")
    else:
        print("No updates available.")

if __name__ == "__main__":
    main()
