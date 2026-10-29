from datetime import datetime
import os
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
import pandas as pd
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")

app = Flask(__name__)
app.secret_key = "abc123"  

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
USERS_CSV = "users.csv"
CSV_FILE = "file_metadata.csv"

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(USERS_CSV):
  df_users = pd.DataFrame(columns=["username", "password"])
  df_users.to_csv(USERS_CSV, index=False)


def generate_file_type_chart():
  if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
    return None

  try:
    df = pd.read_csv(CSV_FILE)
    if df.empty or "Filename" not in df.columns:
      return None

    df["Extension"] = (
        df["Filename"].apply(lambda x: x.split(".")[-1].upper() if "." in str(x) else "OTHER"))
    type_counts = df["Extension"].value_counts()

    if type_counts.empty:
      return None

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#ea580c", "#fdba74", "#fed7aa", "#94a3b8"]
    type_counts.plot(
        kind="bar", ax=ax, color=colors[: len(type_counts)], edgecolor="#c2410c"
    )

    ax.set_title(
        "Shared Files by Type", fontsize=11, fontweight="bold", color="#0f172a"
    )
    ax.set_xlabel("File Extension", fontsize=10, color="#64748b")
    ax.set_ylabel("Count", fontsize=10, color="#64748b")
    ax.set_facecolor("#ffffff")
    fig.patch.set_facecolor("#ffffff")
    plt.xticks(rotation=0)
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format="png", transparent=True, dpi=120)
    img.seek(0)
    plt.close(fig)
    return base64.b64encode(img.getvalue()).decode("utf8")
  
  except Exception:
    return None


def format_file_size(size_bytes):
  if size_bytes < 1024:
    return f"{size_bytes} B"
  elif size_bytes < 1024 * 1024:
    return f"{round(size_bytes / 1024, 1)} KB"
  else:
    return f"{round(size_bytes / (1024 * 1024), 2)} MB"


@app.route("/")
def index():
  all_files = []
  my_files = []
  other_files = []

  if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
    try:
      df = pd.read_csv(CSV_FILE)
      df = df.iloc[::-1]
      all_files = df.to_dict(orient="records")

      if "user" in session:
        current_user = session["user"]
        my_files = [f for f in all_files if f.get("Uploaded_By") == current_user]
        other_files = [
            f for f in all_files if f.get("Uploaded_By") != current_user
        ]
    except pd.errors.EmptyDataError:
      all_files = []

  chart_url = generate_file_type_chart()

  return render_template(
      "index.html",
      files=all_files,
      my_files=my_files,
      other_files=other_files,
      chart_url=chart_url,
  )


@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
      flash("All fields are required.", "error")
      return redirect(url_for("register"))

    if os.path.exists(USERS_CSV) and os.path.getsize(USERS_CSV) > 0:
      df = pd.read_csv(USERS_CSV, dtype=str)
    else:
      df = pd.DataFrame(columns=["username", "password"])

    if username in df["username"].values:
      flash("Username already taken. Choose another.", "error")
      return redirect(url_for("register"))

    new_user = pd.DataFrame([{"username": username, "password": password}])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("login"))

  return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if os.path.exists(USERS_CSV) and os.path.getsize(USERS_CSV) > 0:
      df = pd.read_csv(USERS_CSV, dtype=str)
      df["username"] = df["username"].str.strip()
      df["password"] = df["password"].str.strip()
    else:
      df = pd.DataFrame(columns=["username", "password"])

    user_row = df[(df["username"] == username) & (df["password"] == password)]

    if not user_row.empty:
      session["user"] = username
      flash(f"Welcome back, {username}!", "success")
      return redirect(url_for("index"))
    else:
      flash("Invalid username or password.", "error")
      return redirect(url_for("login"))

  return render_template("login.html")


@app.route("/logout")
def logout():
  session.pop("user", None)
  flash("Logged out successfully.", "success")
  return redirect(url_for("index"))


@app.route("/upload", methods=["POST"])
def upload():
  if "user" not in session:
    flash("You must be logged in to upload files.", "error")
    return redirect(url_for("login"))

  file_obj = request.files.get("file")

  if file_obj and file_obj.filename != "":
    filename = secure_filename(file_obj.filename)
    if not filename:
      flash("Invalid filename. Please rename and try again.", "error")
      return redirect("/")

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file_obj.save(file_path)

    raw_size = os.path.getsize(file_path)
    file_size_str = format_file_size(raw_size)
    upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame([{
        "Filename": filename,
        "Uploaded_By": session["user"],
        "Size_KB": file_size_str,
        "Upload_Time": upload_time,
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
  if "user" not in session:
    flash("Unauthorized action. Please log in.", "error")
    return redirect(url_for("login"))

  if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
    df = pd.read_csv(CSV_FILE)
    target = df[df["Filename"] == filename]

    if not target.empty:
      file_owner = str(target.iloc[0]["Uploaded_By"]).strip()

      if session["user"] == file_owner:
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
        flash("You can only delete files that you uploaded!", "error")

  return redirect("/")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)