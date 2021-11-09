
import os
import activate
from flask import Flask, jsonify, render_template, request, redirect, url_for
import  zipfile
import sqlite3
import datetime



class knownFacesLabels():
    def __init__(self,face_image_path):
        self.face_image_path = face_image_path
        self.label = str(self.face_image_path).split(".", maxsplit=1)[0]
    