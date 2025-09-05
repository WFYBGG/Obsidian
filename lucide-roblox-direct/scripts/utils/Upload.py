# 
# Generic script to upload assets to Roblox using the Open Cloud API
# Made by claude
#

import argparse
import os
import time
import requests

    
asset_type_map = {
    '.png': 'Decal',
    '.jpg': 'Decal',
    '.jpeg': 'Decal',
    '.gif': 'Decal',
    '.bmp': 'Decal',
    '.tga': 'Decal',
    '.mp3': 'Audio',
    '.ogg': 'Audio',
    '.wav': 'Audio',
    '.fbx': 'Model',
    '.obj': 'Model'
}

def upload_asset(file_path, name, description, auth_token, creator_id, creator_type="user"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    asset_type = asset_type_map.get(file_ext)
    if not asset_type:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    # Roblox Open Cloud API endpoint
    url = "https://apis.roblox.com/assets/v1/assets"
    
    # Prepare headers
    headers = {
        "x-api-key": auth_token,
    }
    
    # Prepare the request payload with creator information
    creator_key = "userId" if creator_type.lower() == "user" else "groupId"
    request_data = {
        "assetType": asset_type,
        "displayName": name,
        "description": description,
        "creationContext": {
            "creator": {
                creator_key: str(creator_id)
            }
        }
    }
    
    # Prepare the multipart form data
    with open(file_path, 'rb') as file:
        import json
        files = {
            'request': (None, json.dumps(request_data), 'application/json'),
            'fileContent': (os.path.basename(file_path), file, 'application/octet-stream')
        }
        
        try:
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operationId')

                while True:
                    time.sleep(0.25)
                    status_url = f"https://apis.roblox.com/assets/v1/operations/{operation_id}"
                    status_response = requests.get(status_url, headers=headers)
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        if status_result.get('done') == True:
                            print(status_result["response"]["assetId"])
                            break
                    else:
                        print(f"❌ Failed to check operation status: {status_response.status_code}")
                        return None


                return result
            else:
                print(f"❌ Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None


def main():
    """Main function to handle command line arguments and execute upload"""
    parser = argparse.ArgumentParser(
        description="Upload assets to Roblox using Open Cloud API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload.py image.png --name "My Image" --description "A cool image" --auth "your_api_key" --creator-id "123456789"
  python upload.py sound.mp3 --name "Background Music" --description "Epic soundtrack" --auth "your_api_key" --creator-id "123456789" --creator-type "user"
  python upload.py model.fbx --name "3D Model" --description "Cool 3D model" --auth "your_api_key" --creator-id "987654321" --creator-type "group"
        """
    )
    
    parser.add_argument(
        'file_path',
        help='Path to the file to upload'
    )
    
    parser.add_argument(
        '--name',
        required=True,
        help='Name for the asset'
    )
    
    parser.add_argument(
        '--description',
        required=True,
        help='Description for the asset'
    )
    
    parser.add_argument(
        '--auth',
        required=True,
        help='Roblox Open Cloud API key'
    )
    
    parser.add_argument(
        '--creator-id',
        required=True,
        help='Creator ID (user ID or group ID)'
    )
    
    parser.add_argument(
        '--creator-type',
        choices=['user', 'group'],
        default='user',
        help='Creator type: user or group (default: user)'
    )
    
    args = parser.parse_args()
    
    try:
        result = upload_asset(args.file_path, args.name, args.description, args.auth, args.creator_id, args.creator_type)
        if result:
            exit(0)  # Success
        else:
            exit(1)  # Failure
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
