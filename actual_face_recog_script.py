import numpy as np
import cv2
import face_recognition
import io
import os
from googleapiclient.http import MediaIoBaseDownload
from Google import Create_Service
cascades=cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')
scopes=['https://www.googleapis.com/auth/drive']
api_ver='v3'
client_file='client_secret_file.json'
api_name='drive'
service=Create_Service(client_file,api_name,api_ver,scopes)
names=[]
def get_folder_id(service,name):
    results=service.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id)",spaces='drive').execute()
    items=results.get('files',[])
    return items[0]['id'] if items else None
def get_file_id(service,name):
    query=f"name='{name}' and trashed=false"
    results=service.files().list(q=query,spaces='drive').execute()
    files=results.get('files',[])
    return files[0]['id'] if files else None
parent_folder_name=input("Pls enter the name of the folder which you wish to sort:")
image_name=input("Pls enter the image name you wish to scan (preferably one where everyone is present):")
parent_id=get_folder_id(service,parent_folder_name)
image_id=get_file_id(service,image_name)
def crop(image_name):
    print("crop called")
    image=cv2.imread(image_name)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    faces=cascades.detectMultiScale(gray,scaleFactor=1.05,minNeighbors=4)
    i=0
    for x,y,w,h in faces:
        print(i,x,y,w,h)
        cropped_image=image[y:y+h,x:x+w]
        target_file_name=f'stored-faces/{i}'+'.jpg'
        cv2.imwrite(target_file_name,cropped_image)
        img=cv2.imread(target_file_name)
        rgb_img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        location=face_recognition.face_locations(rgb_img)
        encoding=face_recognition.face_encodings(rgb_img,location)
        if encoding:
            names.append(i)
            i=i+1
            print("one face detected!")
        else:
            os.remove(target_file_name)
    for name in names:
        file_metadata={'name':name,'parents':[parent_id],'mimeType':'application/vnd.google-apps.folder'}
        service.files().create(body=file_metadata).execute()
def download_image(service,file_id):
    request=service.files().get_media(fileId=file_id)
    fh=io.BytesIO()
    downloader=MediaIoBaseDownload(fd=fh,request=request)
    done=False
    while not done:
        status,done=downloader.next_chunk()
        print("Download progress:{0}".format(status.progress()*100))
    fh.seek(0)
    with open(os.path.join("C:/Users/LENOVO/Desktop/IIIT PUNE/vacation work/google drive image recognizer",image_name),'wb') as f:
        f.write(fh.read())
        f.close()
query=f"parents='{parent_id}'"
results=service.files().list(q=query).execute()
files=results.get('files')
for file in files:
    if file['mimeType']=='image/jpeg' and file['name']==image_name:
        download_image(service,image_id)
        crop(image_name)
