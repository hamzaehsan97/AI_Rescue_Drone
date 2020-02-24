from flask import Flask, jsonify, render_template, request, redirect, url_for
import os, zipfile
import sqlite3
import datetime





# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)


# sanity check route
@app.route('/')
def index():
    return render_template('index.html')


app.config[
    'UPLOAD_FOLDER'] = "/Users/hamzaehsan/Desktop/drone/drone/img/upload"

#Upload files to backend
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():

    msg=""
    if request.method == 'POST':
        print("POST True")
        if request.files:
            print("file True")
            file = request.files["image"]
            try:
                name = request.form["name"]
            except:
                name = "default name"
                msg = "error in getting name"
                return render_template("uploaded.html",msg = msg)
            time = datetime.datetime.now()
            time = str(time)
            try:
                fileName = (str(file.filename))
                fileName = fileName.split(".", maxsplit=1)[1]
                fileName = name + "." + fileName
                file.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], fileName))
                print(fileName+" has been uploaded")
                connection = sqlite3.connect('database.db')
                cursor = connection.cursor()
                cursor.execute("INSERT INTO people(name, found, time, fileName) VALUES(?,?,?,?)",(name, "FALSE", time, fileName))
                connection.commit()
                msg = "Recorded to database"
                connection.close()
                msg="File has been saved"
                return render_template("uploaded.html",msg = msg)
            except:
                msg = "Error in database insertion"
                return render_template("uploaded.html",msg = msg)
        else:
            print("POST True, file not saved.")
            msg="request.files return FALSE"
    else:
        print("File not saved")
    return render_template('uploaded.html',msg=msg)
   


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
