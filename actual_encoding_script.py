from Google import Create_Service
import os
import cv2
import numpy as np
from PIL import Image
import face_recognition
import cv2
import io
from googleapiclient.http import MediaIoBaseDownload
cascades=cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')
known_faces={}
CLIENT_SECRET_FILE="client_secret_file.json"
API_NAME='drive'
API_VERSION='v3'
SCOPES=["https://www.googleapis.com/auth/drive"]
service=Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
def get_folder_id(service,name):
    results=service.files().list(q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",spaces='drive',fields="files(id)").execute()
    items=results.get('files',[])
    return items[0]['id'] if items else None
for filename in os.listdir("stored-faces"):
    img_path=os.path.join("stored-faces",filename)
    image=face_recognition.load_image_file(img_path)
    encodings=face_recognition.face_encodings(image)
    if encodings:
        label=os.path.splitext(filename)[0]
        known_faces[label]=encodings[0]
def euclidean_distance(e1,e2):
    return np.linalg.norm(e1-e2)
parent_folder_name=input("Enter folder name: ")
parent_id=get_folder_id(service,parent_folder_name)
files=[]
page_token=None
query=f"'{parent_id}' in parents and mimeType='image/jpeg' and trashed=false"
while True:
    response=service.files().list(q=query,spaces='drive',fields='nextPageToken, files(id,name,mimeType)',pageToken=page_token).execute()
    files.extend(response.get('files',[]))
    page_token=response.get('nextPageToken',None)
    if page_token is None:
        break
for file in files:
    file_id=file['id']
    temp_filename=f"temp_{file['name']}"
    request=service.files().get_media(fileId=file_id)
    with io.FileIO(temp_filename,'wb') as fh:
        downloader=MediaIoBaseDownload(fh,request)
        done=False
        while not done:
            status,done=downloader.next_chunk()
    print(f"Downloaded to: {temp_filename}")
    image=cv2.imread(temp_filename)
    rgb_image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    matched_labels=set()
    face_location=face_recognition.face_locations(rgb_image)
    encodings=face_recognition.face_encodings(rgb_image,face_location)
    for encoding in encodings:
        for label,known_encoding in known_faces.items():
            dist=euclidean_distance(encoding,known_encoding)
            if dist<=0.47:
                matched_labels.add(label)
    print(f"Matched labels: {matched_labels}")
    for label in matched_labels:
        try:
            target_id=get_folder_id(service,label)
            file_metadata={'name':file['name'],'parents':[target_id]}
            service.files().copy(fileId=file_id,body=file_metadata).execute()
            print(f"Photo added:'{file['name']}' to label:{label}")
            print(f"temp file used: {temp_filename}")
        except Exception as e:
            print(f"Failed to copy '{file['name']}' to folder: '{label}':{e}")
    os.remove(temp_filename)
