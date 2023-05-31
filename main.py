
from flask import Flask, flash, request, redirect
from werkzeug.utils import secure_filename
from boto_client import initialize_client
from botocore import exceptions


ALLOWED_EXTENSIONS = {"csv"}
BUCKET_NAME = "clasebucket"

client = initialize_client()

app = Flask(__name__)


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return "Hello World!"


@app.route("/files", methods=["GET", "POST", "UPDATE", "DELETE"])
def crud_files():
    if request.method == "GET":
        try:
            file_name = request.form["file"]

            client.download_file(Bucket=BUCKET_NAME,
                                 Key=file_name, Filename=file_name)

            return "success!", 200
        except exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return "object does not exist!", 404
            else:
                return "internal server error!", 500

    if request.method == "DELETE":
        try:
            file_name = request.form["file"]

            client.delete_object(
                Bucket=BUCKET_NAME,
                Key=file_name,
            )

            return "success!", 200
        except exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return "object does not exist!", 404
            else:
                return "internal server error!", 500

    if request.method == "POST" or "UPDATE":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            file_name = secure_filename(file.filename)
            client.put_object(
                Body=file,
                Bucket=BUCKET_NAME,
                Key=file_name
            )
            return "success!", 200


if __name__ == "__main__":
    app.run(host="localhost", port=3000)
