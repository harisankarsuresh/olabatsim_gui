import os
import subprocess


def run():
    path_to_app = os.path.join(os.path.dirname(__file__), "app.py")
    subprocess.run(["streamlit", "run", path_to_app])


if __name__ == "__main__":
    run()
