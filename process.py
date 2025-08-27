import numpy as np
import cv2
import face_recognition
import io
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cascade_path = os.path.join(BASE_DIR, 'cascades','data','haarcascade_frontalface_default.xml')
cascades = cv2.CascadeClassifier(cascade_path)
from googleapiclient.http import MediaIoBaseDownload
def get_folder_id(service,name):
    results=service.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id)",spaces='drive').execute()
    items=results.get('files',[])
    return items[0]['id'] if items else None
def process_images(service,cascades,parent_id,image_id,main_photo):
    stored_faces_path=os.path.join(BASE_DIR,'static','stored-faces')
    os.makedirs(stored_faces_path,exist_ok=True)
    for f in os.listdir(stored_faces_path):
        try:
            os.remove(os.path.join(stored_faces_path,f))
        except Exception as e:
            print("Could not delete")
    def crop(image_path):
            names=[]
            print("crop called")
            image=cv2.imread(image_path)
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            faces=cascades.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5)
            i=0
            for x,y,w,h in faces:
                print(i,x,y,w,h)
                cropped_image=image[y:y+h,x:x+w]
                target_file_name=f'static/stored-faces/{i}'+'.jpg'
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
        SAVE_DIR = os.path.join(BASE_DIR, "downloads")
        os.makedirs(SAVE_DIR, exist_ok=True)
        save_path = os.path.join(SAVE_DIR, main_photo)
        with open(save_path,'wb') as f:
            f.write(fh.read())
            f.close()
        return save_path
    query=f"parents='{parent_id}'"
    results=service.files().list(q=query).execute()
    files=results.get('files')
    for file in files:
        if file['mimeType']=='image/jpeg' and file['name']==main_photo:
            save_path=download_image(service,image_id)
            crop(save_path)
    known_faces={}
    for filename in os.listdir("static/stored-faces"):
        img_path=os.path.join("static/stored-faces",filename)
        image=face_recognition.load_image_file(img_path)
        encodings=face_recognition.face_encodings(image)
        if encodings:
            label=os.path.splitext(filename)[0]
            known_faces[label]=encodings[0]
    def euclidean_distance(e1,e2):
        return np.linalg.norm(e1-e2)
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
    return "Successfully sorted the folder!"
