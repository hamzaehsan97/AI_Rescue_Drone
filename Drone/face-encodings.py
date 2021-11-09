
import face_recognition


class faceEncoding():
    def __init__(self,face_image_path):
        self.face_image_path = face_image_path
        self.face_image = face_recognition.load_image_file(self.face_image_path)
        self.face_encoding = face_recognition.face_encodings(self.face_image)[0]
    