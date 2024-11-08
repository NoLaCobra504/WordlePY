import os
import requests
import zipfile
import shutil
import json

# Define the GitHub repository details
GITHUB_REPO = 'https://raw.githubusercontent.com/yourusername/yourrepository/main/'

CURRENT_VERSION = "1.0.0"  # This should match the version in wordle_game.py

def check_for_update():
    try:
        # Make a GET request to fetch the latest version data
        response = requests.get(GITHUB_REPO + 'latest_version.json')

        # Log the raw response for debugging purposes
        print(f"Raw response from server: {response.text[:200]}")  # Limit log output for brevity

        # Check if the response contains JSON
        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON response: {e}")
                return None
        else:
            print(f"Expected JSON, but got: {response.headers.get('Content-Type')}")
            print(f"Response text: {response.text[:200]}")  # Show first 200 chars of response for debugging
            return None

        # Check if 'version' exists in the JSON response
        latest_version = response_data.get('version')

        if not latest_version:
            print("No version information found in the response.")
            return None

        # Assuming version is in 'major.minor.patch' format, compare numerically
        current_version_parts = [int(part) for part in CURRENT_VERSION.split('.')]
        latest_version_parts = [int(part) for part in latest_version.split('.')]

        if latest_version_parts > current_version_parts:
            return latest_version
        return None

    except requests.RequestException as e:
        # Handle network-related errors or issues with the GET request
        print(f"Update check failed: {e}")
        return None

def download_update(latest_version):
    try:
        url = f'{GITHUB_REPO}updates/your_app_{latest_version}.zip'
        response = requests.get(url, allow_redirects=True)
        
        with open(f'update_{latest_version}.zip', 'wb') as file:
            file.write(response.content)
        
        return f'update_{latest_version}.zip'
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
