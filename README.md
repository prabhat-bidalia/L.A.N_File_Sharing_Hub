# 📁 LAN File Sharing Hub

A lightweight, secure local web application built with Python (Flask), Pandas, and Matplotlib designed for seamless file sharing, user management, and visual analytics within a local area network (LAN).

## 🚀 Features

- **Session-Based Authentication:** Secure user registration and login system (`users.csv`) powered by Flask sessions to track file ownership.
- **File Uploads & Validation:** Securely upload files up to 50 MB with automatic filename sanitization (`secure_filename`) and timestamp generation.
- **Organized Dashboard Views:** Separate tables displaying personal uploaded files alongside resources shared by other peers on the network.
- **Access Control & Deletion:** Built-in permissions ensuring users can only delete files they personally uploaded.
- **Visual Data Analytics:** Integrated Matplotlib chart dynamically generating a breakdown of shared file types across the network.
- **Lightweight Storage:** Zero heavy databases required—all metadata and user credentials are managed efficiently via Pandas and local CSV files.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Data Processing & Storage:** Pandas, CSV
- **Data Visualization:** Matplotlib
- **Frontend:** HTML5, CSS3 

---
## 💻 Setup & Installation

1. **Clone the repository:** `git clone https://prabhat261-admin@bitbucket.org/prabhat26/l.an_file_sharing_hub.git`
2. **Navigate into the folder** `cd l.a.n_file_sharing_hub`
3. **Run the application** `python app.py`
