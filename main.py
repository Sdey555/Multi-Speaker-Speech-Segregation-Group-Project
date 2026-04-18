import os

from config import OUTPUT_FOLDER
from GUI.app import launch_gui


def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    launch_gui()

if __name__ == "__main__":
    main()
