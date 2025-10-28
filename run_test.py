import subprocess

# Jalankan test Playwright
subprocess.run("pytest --html=reports/test_report.html --self-contained-html", shell=True)

# Jalankan push otomatis ke GitHub
subprocess.run("python push_report.py", shell=True)
