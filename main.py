import subprocess
import os
import sys
import webbrowser
import time

def launch_streamlit():
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    # Launch streamlit as a separate process
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", app_path])

    # Open browser once after short delay
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    launch_streamlit()
