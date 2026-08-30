import argparse
import http.client
import httplib2
import os
import random
import sys
import time

import google.auth.exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# YouTube API upload scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

# Explicitly tell the underlying HTTP transport library not to retry
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up
MAX_RETRIES = 10

# Always retry when these exceptions are raised
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

# Always retry when an apiclient.errors.HttpError with one of these status codes is raised
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

def get_authenticated_service(client_secret_file="client_secret.json", token_file="token.json"):
    """
    Authenticates against YouTube Data API v3.
    Uses token.json if present; otherwise prompts one-time browser login using client_secret.json.
    """
    creds = None
    
    # Locate token file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, token_file) if not os.path.isabs(token_file) else token_file
    secret_path = os.path.join(base_dir, client_secret_file) if not os.path.isabs(client_secret_file) else client_secret_file

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"⚠️ [AUTH] Existing token invalid: {e}. Re-authenticating...")

    # If there are no valid credentials available, request login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 [AUTH] Refreshing expired OAuth token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ [AUTH] Refresh failed: {e}. Launching browser authorization...")
                creds = None

        if not creds:
            if not os.path.exists(secret_path):
                raise FileNotFoundError(
                    f"❌ [AUTH ERROR] '{client_secret_file}' not found.\n"
                    f"👉 Please download your OAuth 2.0 Client ID JSON from Google Cloud Console and place it as '{secret_path}'."
                )
            
            print("🌐 [AUTH] Opening browser for one-time Google OAuth authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future headless runs
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print(f"💾 [AUTH] Token cached to '{token_path}'. Future uploads will run headlessly!")

    return build('youtube', 'v3', credentials=creds)

def upload_video(
    youtube,
    file_path,
    title,
    description="",
    tags=None,
    category_id="1",  # 1 = Film & Animation, 24 = Entertainment
    privacy_status="unlisted",
    publish_at=None,
    thumbnail_path=None
):
    """
    Uploads a video file to YouTube using resumable chunked upload.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    tags_list = [t.strip() for t in tags.split(',')] if isinstance(tags, str) else (tags or [])

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags_list,
            'categoryId': str(category_id)
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    if publish_at and privacy_status == "private":
        # Format: YYYY-MM-DDThh:mm:ss.sZ
        body['status']['publishAt'] = publish_at

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    print(f"\n=================================================================")
    print(f"🚀 Starting YouTube Upload: {os.path.basename(file_path)}")
    print(f"📌 Title: {title}")
    print(f"🔒 Privacy: {privacy_status}")
    print(f"📊 Size: {file_size_mb:.2f} MB")
    print(f"=================================================================\n")

    # 8MB chunk size for high-speed reliable resumable upload
    chunk_size = 8 * 1024 * 1024
    media = MediaFileUpload(file_path, chunksize=chunk_size, resumable=True)

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    error = None
    retry = 0
    t_start = time.time()

    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                uploaded_mb = (status.resumable_progress or 0) / (1024 * 1024)
                elapsed = max(0.1, time.time() - t_start)
                speed = uploaded_mb / elapsed
                print(f"⏳ Upload Progress: {progress:3d}% ({uploaded_mb:.1f}/{file_size_mb:.1f} MB @ {speed:.2f} MB/s)", flush=True)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise e
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            print(f"⚠️ {error}")
            retry += 1
            if retry > MAX_RETRIES:
                raise RuntimeError("No longer attempting to retry. Upload aborted.")
            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f"Sleeping {sleep_seconds:.1f} seconds and then retrying...")
            time.sleep(sleep_seconds)
            error = None

    video_id = response.get('id')
    video_url = f"https://youtu.be/{video_id}"
    print(f"\n=================================================================")
    print(f"🎉 SUCCESS! Video Upload Complete!")
    print(f"🆔 Video ID: {video_id}")
    print(f"🔗 URL: {video_url}")
    print(f"=================================================================\n")

    # Upload custom thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"🖼️ Uploading custom thumbnail: {thumbnail_path}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("✅ Custom thumbnail attached successfully!")
        except Exception as te:
            print(f"⚠️ Thumbnail upload warning: {te}")

    return response

def main():
    parser = argparse.ArgumentParser(description="YouTube Data API v3 Video Uploader")
    parser.add_argument("--check-auth", action="store_true", help="Validate OAuth2 authentication status")
    parser.add_argument("--secret", default="client_secret.json", help="Path to client_secret.json")
    parser.add_argument("--token", default="token.json", help="Path to token.json")
    parser.add_argument("--file", help="Path to video file to upload")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--category", default="1", help="Category ID (1 = Animation, 24 = Entertainment)")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "private", "unlisted"], help="Privacy status")
    parser.add_argument("--publish-at", help="Scheduled publish time (ISO format)")
    parser.add_argument("--thumbnail", help="Path to custom thumbnail image")

    args = parser.parse_args()

    if args.check_auth:
        print("🔍 Checking YouTube API authentication status...")
        try:
            yt = get_authenticated_service(client_secret_file=args.secret, token_file=args.token)
            channels = yt.channels().list(part="snippet", mine=True).execute()
            items = channels.get("items", [])
            if items:
                ch_title = items[0]["snippet"]["title"]
                print(f"✅ Authenticated successfully! Connected Channel: '{ch_title}'")
            else:
                print("✅ Authenticated successfully (No primary channel created yet).")
        except Exception as e:
            print(f"❌ Auth check failed: {e}")
        return

    if not args.file:
        print("Usage: python youtube_uploader.py --file <video.mp4> --title 'Title' [options]")
        print("Run with --check-auth to verify credentials.")
        return

    yt = get_authenticated_service(client_secret_file=args.secret, token_file=args.token)
    title = args.title or os.path.splitext(os.path.basename(args.file))[0]
    upload_video(
        youtube=yt,
        file_path=args.file,
        title=title,
        description=args.description,
        tags=args.tags,
        category_id=args.category,
        privacy_status=args.privacy,
        publish_at=args.publish_at,
        thumbnail_path=args.thumbnail
    )

if __name__ == "__main__":
    main()
