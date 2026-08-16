# 📁 File Sharing Hub

A lightweight, PIN-protected web application for sharing files across local networks without forcing user sign-ups.

**Key Features**
* **Zero-Account PIN Security:** Users create a unique 4-digit PIN on upload to delete their files anytime.
* **LAN Access:** Runs locally across all devices (phones, laptops, tablets) on the same Wi-Fi network.
* **Lightweight Storage:** Tracks metadata directly in a CSV file using Pandas—no database setup required.
* **Upload Security:** Sanitizes filenames using `secure_filename()` and limits uploads to 50 MB.

**Tech Stack**
* **Backend:** Python 3, Flask, Pandas
* **Frontend:** HTML5, CSS3

**Quick Start**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/prabhat-bidalia/L.A.N_File_Sharing_Hub
   cd file-sharing-hub
