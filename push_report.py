import os
import subprocess
from datetime import datetime

# Folder report
REPORT_DIR = "reports"

# Pastikan folder reports ada
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

# Buat commit message pakai timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
commit_message = f"Update report {timestamp}"

# Jalankan perintah git
commands = [
    "git add reports/",
    f'git commit -m "{commit_message}"',
    "git push origin main"
]

for cmd in commands:
    try:
        print(f"Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"⚠️ Command failed or nothing to commit: {cmd}")
