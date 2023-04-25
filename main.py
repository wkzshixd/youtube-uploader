import json
import os
import time
 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
 
API_KEY = 'AIzaSyDVQctH9FIzyVdYWli-73True8ZC1Kpyss'
 
APP_TOKEN_FILE = "Y:\projects\$$$\youtube_uploader\src\client_secret.json"
USER_TOKEN_FILE = "Y:\projects\$$$\youtube_uploader\wkzkey.json"
 
SCOPES = ['https://www.googleapis.com/auth/youtube', 'https://www.googleapis.com/auth/userinfo.profile']
 
def get_creds_cons():
    flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
    return flow.run_console()
 

def get_creds_saved():
    creds = None
    if os.path.exists(USER_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
 
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
 
        with open(USER_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
 
    return creds
 
#Get YouTube API service w API Key only
def get_service_creds(platform, version):
    #creds = get_creds_cons()
    creds = get_creds_saved()
    service = build(platform, version, credentials=creds)
    return service
 

def video_upload(video_path, title, **kwargs):
    print("** upload video")
 
    # chunksize размер блока в БАЙТАХ (int), чем хуже соединение, тем мельче блок
    # напр. для мобильного трафа норм 1024*1024*3 = 3М
    # -1 => видос будет грузиться целиком, быстрее на норм сети и при обрыве все равно будет докачка
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
 
    # список полей см здесь https://developers.google.com/youtube/v3/docs/videos/insert
    meta = {
        'snippet': {
            'title' : title,
            'description' : kwargs.get("description", "empty desc")
        },
        # All videos uploaded via the videos.insert endpoint from unverified API projects created after 28 July 2020
        # will be restricted to private viewing mode. To lift this restriction,
        # each API project must undergo an audit to verify compliance
        # --- т.е. для прилки в статусе теста тут всегда приват, иначе видос будет заблокирован
        'status':{
            'privacyStatus':kwargs.get("privacy", "private")
        }
    }
 
    insert_request = get_service_creds("youtube", "v3").videos().insert(
        part=','.join(meta.keys()),
        body=meta,
        media_body=media
    )
 
    r = resumable_upload(insert_request)
 
    print(r)
 

def resumable_upload(request, retries = 5):
    while retries > 0:
        try:
            status, response = request.next_chunk()
            if response is None: continue # next chunk, will be None until the resumable media is fully uploaded
            if 'id' not in response: raise Exception("no id found while video uploading")
 
            return response # success
        except Exception as e:
            print(e)
            retries -= 1
            time.sleep(5)
 
    return None


if __name__ == '__main__':
    print("////////////////////////////////////\n")
    print("// created and fucked over by wkz //\n")
    print("////////////////////////////////////\n")
    video_upload(r"misc\xd.mkv", "did it!")