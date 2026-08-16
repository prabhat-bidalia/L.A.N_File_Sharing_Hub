
import os
import pandas as pd
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "abc123"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
CSV_FILE = "file_metadata.csv"

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def format_file_size(size_bytes):
  if size_bytes < 1024:
    return f"{size_bytes} B"
  elif size_bytes < 1024 * 1024:
    return f"{round(size_bytes / 1024, 1)} KB"
  else:
    return f"{round(size_bytes / (1024 * 1024), 2)} MB"

@app.route("/")
def index():
  file_list = []
  if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
    try:
      df = pd.read_csv(CSV_FILE, dtype={"PIN": str})
      df["PIN"] = df["PIN"].astype(str).str.strip().str.zfill(4)
      file_list = df.to_dict(orient="records")
    except pd.errors.EmptyDataError:
      file_list = []

  return render_template("index.html", files=file_list)


@app.route("/upload", methods=["POST"])
def upload():
  uploader_name = request.form.get("uploader", "").strip()
  uploader_pin = request.form.get("pin", "").strip()
  file_obj = request.files.get("file")

  if not uploader_pin.isdigit() or len(uploader_pin) != 4:
    flash("PIN must be exactly 4 digits.", "error")
    return redirect("/")

  if file_obj and file_obj.filename != "":
    filename = secure_filename(file_obj.filename)
    if not filename:
      flash("Invalid filename. Please rename the file and try again.", "error")
      return redirect("/")

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file_obj.save(file_path)

    raw_size = os.path.getsize(file_path)
    file_size_str = format_file_size(raw_size)
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame([{
        "Filename": filename,
        "Uploaded_By": uploader_name if uploader_name else "Anonymous",
        "Size_KB": file_size_str,
        "Upload_Time": upload_time,
        "PIN": uploader_pin.zfill(4),
    }])

    file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
    new_row.to_csv(CSV_FILE, mode="a", index=False, header=not file_exists)

    flash("File uploaded successfully!", "success")
  else:
    flash("Please select a valid file.", "error")

  return redirect("/")


@app.route("/download/<filename>")
def download_file(filename):
  return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
  user_pin = request.form.get("pin", "").strip()

  if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
    df = pd.read_csv(CSV_FILE, dtype={"PIN": str})
    target = df[df["Filename"] == filename]

    if not target.empty:
      stored_pin = str(target.iloc[0]["PIN"]).strip().zfill(4)

      if user_pin == stored_pin:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
          os.remove(file_path)

        df = df[df["Filename"] != filename]
        if df.empty:
          os.remove(CSV_FILE)
        else:
          df.to_csv(CSV_FILE, index=False)

        flash("File deleted successfully!", "success")
      else:
        flash("Incorrect PIN. File not deleted.", "error")

  return redirect("/")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
