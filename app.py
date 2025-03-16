# from flask import Flask, request, jsonify
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# import yt_dlp
# from datetime import datetime
# import pytz
# import os
# from tqdm import tqdm
# from flask_cors import CORS
# import os


# app = Flask(__name__)
# CORS(app)

# SCOPES = [
#     'https://www.googleapis.com/auth/youtube.upload',
#     'https://www.googleapis.com/auth/youtube.force-ssl'
# ]


# def get_authenticated_service():
#     credentials = None
#     CLIENT_SECRET_PATH = "/etc/secrets/client_secret.json"
#     TOKEN_PATH = "/etc/secrets/token.json"  # Read the initial token from secrets
#     REFRESH_TOKEN_PATH = "/tmp/refreshed_token.json"  # Write refreshed token here
    
#     # First try to use the refreshed token if it exists
#     if os.path.exists(REFRESH_TOKEN_PATH):
#         credentials = Credentials.from_authorized_user_file(REFRESH_TOKEN_PATH, SCOPES)
#     # Otherwise use the initial token from secrets
#     elif os.path.exists(TOKEN_PATH):
#         credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
#     # If we have credentials but they're expired, refresh them
#     if credentials and credentials.expired and credentials.refresh_token:
#         credentials.refresh(Request())
#         # Save the refreshed token to the writable location
#         with open(REFRESH_TOKEN_PATH, 'w') as token:
#             token.write(credentials.to_json())
#     # If we have no credentials at all, we can't proceed on the server
#     elif not credentials or not credentials.valid:
#         raise Exception("No valid credentials available. Upload a valid token.json to the secrets directory.")
        
#     return build('youtube', 'v3', credentials=credentials)


# # Add the cookie conversion function here
# def convert_json_cookies_to_netscape(json_cookies, output_path):
#     """Convert JSON format cookies to Netscape format for yt-dlp"""
#     try:
#         # Parse the JSON cookies
#         cookies = json.loads(json_cookies) if isinstance(json_cookies, str) else json_cookies
        
#         with open(output_path, 'w') as f:
#             # Write the Netscape cookies file header
#             f.write("# Netscape HTTP Cookie File\n")
#             f.write("# https://curl.haxx.se/docs/http-cookies.html\n")
#             f.write("# This file was generated by Claude! Edit at your own risk.\n\n")
            
#             # Process each cookie
#             for cookie in cookies:
#                 domain = cookie.get('domain', '')
#                 flag = 'TRUE' if cookie.get('hostOnly', False) else 'FALSE'
#                 path = cookie.get('path', '/')
#                 secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
#                 expiration = str(int(cookie.get('expirationDate', 0)))
#                 name = cookie.get('name', '')
#                 value = cookie.get('value', '')
                
#                 # Format: domain flag path secure expiration name value
#                 cookie_line = f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n"
#                 f.write(cookie_line)
        
#         return True
#     except Exception as e:
#         print(f"Error converting cookies: {e}")
#         return False


# def download_video(url, filename="video.mp4"):
#     # Create a temp cookies file in the writable directory
#     json_cookies_path = "/etc/secrets/cookies.json"
#     netscape_cookies_path = "/tmp/cookies.txt"
    
#     # Convert JSON cookies to Netscape format if needed
#     if os.path.exists(json_cookies_path) and not os.path.exists(netscape_cookies_path):
#         try:
#             with open(json_cookies_path, 'r') as f:
#                 json_cookies = f.read()
            
#             print("Converting JSON cookies to Netscape format...")
#             success = convert_json_cookies_to_netscape(json_cookies, netscape_cookies_path)
#             if success:
#                 print(f"Cookies converted successfully to {netscape_cookies_path}")
#             else:
#                 print("Failed to convert cookies")
#         except Exception as e:
#             print(f"Error processing cookies: {e}")
    
#     ydl_opts = {
#         'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
#         'outtmpl': filename,
#         'merge_output_format': 'mp4',
#         'noprogress': True,
#         'quiet': False,  # Set to False to see detailed logs
#         'cookies': netscape_cookies_path,  # Use the converted cookies
#         'sleep-requests': 15,
#         'retries': 15,
#         'max-sleep-interval': 60,
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
#         'nocheckcertificate': True,
#         'ignore-errors': True,
#         'geo-bypass': True
#     }
    
#     try:
#         if os.path.exists(filename):
#             os.remove(filename)
        
#         print(f"Starting download for URL: {url}")
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=True)
#             if info:
#                 print(f"Successfully extracted info for: {info.get('title', 'Unknown')}")
#                 return filename, info.get('title', 'Unknown Title')
#             else:
#                 print("Failed to extract video info")
#                 return None, None
    
#     except Exception as e:
#         print(f"Error downloading video: {e}")
#         return None, None



# def upload_video(filename, title, description="", tags=None, category_id="22", 
#                  privacy_status="private", for_kids=False, schedule_time=None):
#     if tags is None:
#         tags = []

#     print(f"Uploading video: {title}")
#     youtube = get_authenticated_service()

#     status = {'privacyStatus': privacy_status, 'selfDeclaredMadeForKids': for_kids}

#     if schedule_time:
#         status['publishAt'] = schedule_time.isoformat()

#     body = {
#         'snippet': {'title': title, 'description': description, 'tags': tags, 'categoryId': category_id},
#         'status': status
#     }

#     media = MediaFileUpload(filename, chunksize=-1, resumable=True)
#     upload_request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

#     response = None
#     with tqdm(total=100, desc="Uploading", unit="%") as pbar:
#         while response is None:
#             status, response = upload_request.next_chunk()
#             if status:
#                 pbar.update(int(status.progress() * 100) - pbar.n)

#     video_id = response['id']
#     print(f"✅ Upload Complete! Video ID: {video_id}")
#     return video_id


# @app.route('/schedule', methods=['POST'])
# def schedule_upload():
#     data = request.json
#     url = data.get("url")
#     schedule_time = data.get("schedule_time")

#     if not url:
#         return jsonify({"error": "URL is required"}), 400

#     # Try to download the video
#     filename, title = download_video(url)
    
#     # Check if download was successful
#     if filename is None or title is None:
#         return jsonify({
#             "error": "Failed to download video. YouTube might be rate-limiting requests or the cookies are invalid.",
#             "details": "Check your cookies file and ensure it has valid YouTube authentication."
#         }), 500

#     utc_time = None
#     if schedule_time:
#         local_tz = pytz.timezone("Asia/Kolkata")
#         local_time = local_tz.localize(datetime.strptime(schedule_time, "%Y-%m-%d %H:%M"))
#         utc_time = local_time.astimezone(pytz.utc)

#     try:
#         video_id = upload_video(filename, title, schedule_time=utc_time)
#         return jsonify({"message": "Upload scheduled", "video_id": video_id})
#     except Exception as e:
#         return jsonify({"error": f"Upload failed: {str(e)}"}), 500


# @app.route('/delete', methods=['POST'])
# def delete_video():
#     data = request.json
#     video_id = data.get("video_id")

#     if not video_id:
#         return jsonify({"error": "Video ID is required"}), 400

#     try:
#         youtube = get_authenticated_service()
#         youtube.videos().delete(id=video_id).execute()

#         return jsonify({"message": f"Video {video_id} deleted successfully"})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# # if __name__ == '__main__':
# #     app.run(debug=True, port=8000, host='0.0.0.0')
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 8000))  # Use Render's provided port
#     app.run(debug=True, host='0.0.0.0', port=port)





from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import yt_dlp
from datetime import datetime
import pytz
import os
import json  # Added this import
from tqdm import tqdm
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]


def get_authenticated_service():
    credentials = None
    CLIENT_SECRET_PATH = "/etc/secrets/client_secret.json"
    TOKEN_PATH = "/etc/secrets/token.json"  # Read the initial token from secrets
    REFRESH_TOKEN_PATH = "/tmp/refreshed_token.json"  # Write refreshed token here
    
    # First try to use the refreshed token if it exists
    if os.path.exists(REFRESH_TOKEN_PATH):
        credentials = Credentials.from_authorized_user_file(REFRESH_TOKEN_PATH, SCOPES)
    # Otherwise use the initial token from secrets
    elif os.path.exists(TOKEN_PATH):
        credentials = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If we have credentials but they're expired, refresh them
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        # Save the refreshed token to the writable location
        with open(REFRESH_TOKEN_PATH, 'w') as token:
            token.write(credentials.to_json())
    # If we have no credentials at all, we can't proceed on the server
    elif not credentials or not credentials.valid:
        raise Exception("No valid credentials available. Upload a valid token.json to the secrets directory.")
        
    return build('youtube', 'v3', credentials=credentials)


def convert_json_cookies_to_netscape(json_cookies, output_path):
    """Convert JSON format cookies to Netscape format for yt-dlp"""
    try:
        # Parse the JSON cookies
        cookies = json.loads(json_cookies) if isinstance(json_cookies, str) else json_cookies
        
        with open(output_path, 'w') as f:
            # Write the Netscape cookies file header
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.haxx.se/docs/http-cookies.html\n")
            f.write("# This file was generated by Claude! Edit at your own risk.\n\n")
            
            # Process each cookie
            for cookie in cookies:
                domain = cookie.get('domain', '')
                
                # Fix for domain format: add a dot prefix for non-hostOnly cookies
                # This is what's causing the assertion error
                if domain.startswith('.'):
                    initial_dot = True
                    # Domain already has the dot prefix
                else:
                    initial_dot = False
                    # For domains without dot prefix, check if it's hostOnly
                    if not cookie.get('hostOnly', False):
                        domain = '.' + domain
                
                # hostOnly flag is inverted in Netscape format
                flag = 'FALSE' if cookie.get('hostOnly', False) else 'TRUE'
                
                # Ensure flag is consistent with domain format
                if initial_dot:
                    flag = 'TRUE'  # domain_specified should be TRUE for domains with initial dot
                
                path = cookie.get('path', '/')
                secure = 'TRUE' if cookie.get('secure', False) else 'FALSE'
                expiration = str(int(cookie.get('expirationDate', 0)))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                # Format: domain flag path secure expiration name value
                cookie_line = f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n"
                f.write(cookie_line)
        
        return True
    except Exception as e:
        print(f"Error converting cookies: {e}")
        return False


def download_video(url, filename="video.mp4"):
    # Create a temp cookies file in the writable directory
    json_cookies_path = "/etc/secrets/cookies.json"
    netscape_cookies_path = "/tmp/cookies.txt"
    
    # Convert JSON cookies to Netscape format if needed
    if os.path.exists(json_cookies_path):
        try:
            with open(json_cookies_path, 'r') as f:
                json_cookies = f.read()
            
            print("Converting JSON cookies to Netscape format...")
            success = convert_json_cookies_to_netscape(json_cookies, netscape_cookies_path)
            if success:
                print(f"Cookies converted successfully to {netscape_cookies_path}")
            else:
                print("Failed to convert cookies")
        except Exception as e:
            print(f"Error processing cookies: {e}")
            # Continue without cookies as fallback
    
    # Check if cookies file exists
    cookies_exists = os.path.exists(netscape_cookies_path)
    print(f"Cookies file exists: {cookies_exists}")
    
    cookies_file_option = None
    if cookies_exists:
        # Verify cookies file is valid
        try:
            with open(netscape_cookies_path, 'r') as f:
                first_line = f.readline().strip()
                if "Netscape HTTP Cookie File" in first_line:
                    cookies_file_option = netscape_cookies_path
                    cookies_size = os.path.getsize(netscape_cookies_path)
                    print(f"Valid cookies file found, size: {cookies_size} bytes")
                else:
                    print("Invalid cookies file format, will download without cookies")
        except Exception as e:
            print(f"Error reading cookies file: {e}")
    
    ydl_opts = {
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'noprogress': True,
        'quiet': False,  # Set to False to see detailed logs
        'cookiefile': cookies_file_option,  # Only use if valid
        'sleep-requests': 15,
        'retries': 15,
        'max-sleep-interval': 60,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
        'ignore-errors': True,
        'geo-bypass': True
    }
    
    try:
        if os.path.exists(filename):
            os.remove(filename)
        
        print(f"Starting download for URL: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                if info:
                    print(f"Successfully extracted info for: {info.get('title', 'Unknown')}")
                    return filename, info.get('title', 'Unknown Title')
                else:
                    print("Failed to extract video info")
                    return None, None
            except yt_dlp.utils.DownloadError as e:
                # Try once more without cookies if cookies might be the problem
                if cookies_file_option and "cookie" in str(e).lower():
                    print("Cookie error detected, trying download without cookies...")
                    ydl_opts['cookiefile'] = None
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_no_cookies:
                        info = ydl_no_cookies.extract_info(url, download=True)
                        if info:
                            print(f"Successfully downloaded without cookies: {info.get('title', 'Unknown')}")
                            return filename, info.get('title', 'Unknown Title')
                raise  # Re-raise if fallback failed
    
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None, None


def upload_video(filename, title, description="", tags=None, category_id="22", 
                 privacy_status="private", for_kids=False, schedule_time=None):
    if tags is None:
        tags = []

    print(f"Uploading video: {title}")
    youtube = get_authenticated_service()

    status = {'privacyStatus': privacy_status, 'selfDeclaredMadeForKids': for_kids}

    if schedule_time:
        status['publishAt'] = schedule_time.isoformat()

    body = {
        'snippet': {'title': title, 'description': description, 'tags': tags, 'categoryId': category_id},
        'status': status
    }

    media = MediaFileUpload(filename, chunksize=-1, resumable=True)
    upload_request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    with tqdm(total=100, desc="Uploading", unit="%") as pbar:
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                pbar.update(int(status.progress() * 100) - pbar.n)

    video_id = response['id']
    print(f"✅ Upload Complete! Video ID: {video_id}")
    return video_id


@app.route('/schedule', methods=['POST'])
def schedule_upload():
    try:
        data = request.json
        url = data.get("url")
        schedule_time = data.get("schedule_time")

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Try to download the video
        print(f"Attempting to download: {url}")
        filename, title = download_video(url)
        
        # Check if download was successful
        if filename is None or title is None:
            return jsonify({
                "error": "Failed to download video",
                "details": "YouTube might be rate-limiting requests or the video is unavailable. Check your cookies file and ensure it has valid YouTube authentication."
            }), 500

        utc_time = None
        if schedule_time:
            try:
                local_tz = pytz.timezone("Asia/Kolkata")
                local_time = local_tz.localize(datetime.strptime(schedule_time, "%Y-%m-%d %H:%M"))
                utc_time = local_time.astimezone(pytz.utc)
            except Exception as e:
                return jsonify({"error": f"Invalid schedule time format: {str(e)}"}), 400

        try:
            video_id = upload_video(filename, title, schedule_time=utc_time)
            
            # Clean up the downloaded file
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass  # Ignore cleanup errors
                
            return jsonify({
                "message": "Upload successful", 
                "video_id": video_id,
                "title": title,
                "scheduled_time": schedule_time
            })
        except Exception as e:
            return jsonify({"error": f"Upload failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/delete', methods=['POST'])
def delete_video():
    data = request.json
    video_id = data.get("video_id")

    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    try:
        youtube = get_authenticated_service()
        youtube.videos().delete(id=video_id).execute()

        return jsonify({"message": f"Video {video_id} deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))  # Use Render's provided port
    app.run(debug=True, host='0.0.0.0', port=port)
