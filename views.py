import os
import time
from botocore.exceptions import ClientError
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug import secure_filename

from app import app, socketio
import helpers


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file and helpers.file_is_valid(file.filename):
                filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filepath = "tmp/" + filename
                file.save(filepath)
                # flash("Upload successful")
                # try:
                #     upload_res = helpers.upload_to_s3(filepath, filename)
                # except ClientError as e:
                #     # return render_template("error_view.html",
                #     #                        error_message=str(e))
                #     return str(e)
                # try:
                #     transcribe_res = helpers.transcribe(filename)
                # except ClientError as e:
                #     # return render_template("error_view.html",
                #     #                        error_message=str(e))
                #     return str(e)
                # transcript_uri = transcribe_res["TranscriptionJob"][
                #     "Transcript"]["TranscriptFileUri"]
                # session[filename] = helpers.load_json_from_uri(transcript_uri)
                # print("*" * 40)
                # print(transcript_uri)
                # print("*" * 40)
                # #helpers.remove_from_s3(filename)
                # print(f"session var filename{session[filename]}")
                # # return redirect(
                # #     url_for("view_transcript", transcript_id=filename))
                return filename
        flash("Oh no...a file wasn't uploaded.")
        #return redirect(request.url)
        return "No file was uploaded!"


@app.route("/<transcript_id>")
def view_transcript(transcript_id):
    # session["testname"] = {"jobName": "adsf", "results":{"transcripts": [{"transcript":"asdfjkhds hjdsajhsdhjlhjlsda jsdajh"}]}}
    try:
        transcript = helpers.transcript_by_id(transcript_id)
        return render_template(
            "transcript_view.html",
            transcript_title=transcript["transcript_title"],
            transcript_content=transcript["transcript_content"])
    except FileNotFoundError as e:
        return render_template("error_view.html", error_message=str(e))

@socketio.on("upload and transcribe")
def on_upload_and_transcribe(filename):
    socketio.sleep(0)
    try:
        socketio.emit("progress update", "upload started")
        upload_res = helpers.upload_to_s3("tmp/"+filename, filename)
        socketio.sleep(0)
        socketio.emit("progress update", "upload successful")
        socketio.sleep(0)
    except ClientError as e:
        # return render_template("error_view.html",
        #                        error_message=str(e))
        return str(e)
    try:
        socketio.emit("progress update", "transcription started")
        socketio.sleep(0)
        transcribe_res = helpers.transcribe(filename)
        socketio.emit("progress update", "waiting...")
        socketio.sleep(0)
        socketio.emit("progress update", "transcription succesful")
        socketio.sleep(0)
    except ClientError as e:
        # return render_template("error_view.html",
        #                        error_message=str(e))
        return str(e)
    transcript_uri = transcribe_res["TranscriptionJob"][
        "Transcript"]["TranscriptFileUri"]
    session[filename] = helpers.load_json_from_uri(transcript_uri)

    # socketio.sleep(0)
    # socketio.emit("progress update", "upload started")
    # socketio.sleep(2)
    # socketio.emit("progress update", "upload successful")
    # socketio.sleep(5)
    # socketio.emit("progress update", "transcription started")
    # socketio.emit("progress update", "waiting...")
    # socketio.sleep(33)
    # socketio.emit("progress update", "transcription succesful")
    # socketio.sleep(10)
    #transcript_uri = "testname"
    socketio.emit("upload and transcription complete", filename)
    socketio.sleep(0)
