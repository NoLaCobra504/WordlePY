import os
import requests
import zipfile
import shutil
from tqdm import tqdm  # Import tqdm for the progress bar

# Define the GitHub repository details
GITHUB_REPO = 'https://raw.githubusercontent.com/yourusername/yourrepository/main/'

CURRENT_VERSION = "1.0.0"  # This should match the version in wordle_game.py

def check_for_update():
    try:
        response = requests.get(GITHUB_REPO + 'latest_version.json')
        latest_version = response.json().get('version')
        
        if latest_version > CURRENT_VERSION:
            return latest_version
        return None
    except Exception as e:
        print(f"Update check failed: {e}")
        return None

def download_update(latest_version):
    try:
        url = f'{GITHUB_REPO}updates/your_app_{latest_version}.zip'
        response = requests.get(url, stream=True, allow_redirects=True)  # Use stream=True for large files
        
        # Get the total file size for the progress bar
        total_size = int(response.headers.get('content-length', 0))
        
        # Open the file to write the content
        zip_filename = f'update_{latest_version}.zip'
        with open(zip_filename, 'wb') as file, tqdm(
            desc="Downloading update",
            total=total_size,
            unit='B',
            unit_scale=True
        ) as bar:
            # Write the content in chunks and update the progress bar
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))  # Update progress bar with chunk size
        
        return zip_filename
    except Exception as e:
        print(f"Download failed: {e}")
        return None

def extract_update(zip_file):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall('update_folder')
        return 'update_folder'
    except Exception as e:
        print(f"Extraction failed: {e}")
        return None

def replace_files(update_folder):
    try:
        for item in os.listdir(update_folder):
            s = os.path.join(update_folder, item)
            d = os.path.join('.', item)  # Destination is current directory
            
            if os.path.isdir(s):
                shutil.rmtree(d, ignore_errors=True)  # Remove old folder
                shutil.copytree(s, d)  # Copy new folder
            else:
                shutil.copy2(s, d)  # Copy new file

        return True
    except Exception as e:
        print(f"File replacement failed: {e}")
        return False

def main():
    latest_version = check_for_update()
    if latest_version:
        print(f"New version {latest_version} available.")
        
        zip_file = download_update(latest_version)
        if zip_file:
            update_folder = extract_update(zip_file)
            if update_folder:
                if replace_files(update_folder):
                    print("Update successful. Please restart the application.")
                    os.remove(zip_file)  # Clean up the zip file
                    shutil.rmtree(update_folder)  # Clean up the update folder
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

