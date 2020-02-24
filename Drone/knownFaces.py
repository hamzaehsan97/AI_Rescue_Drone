import os
import activate


class faceEncoding():
    def __init__(self,face_image_path):
        self.face_image_path = face_image_path
        
    
    def getEncoding(self, face_image_path):
        face_image = face_recognition.load_image_file(self.face_image_path)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        return face_encoding