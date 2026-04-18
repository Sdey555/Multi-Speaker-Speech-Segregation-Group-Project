import os

# Project Structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "Data")
BIN_DIR = os.path.join(BASE_DIR, "bin")

# FFmpeg Configuration
# This MUST run before any pydub import happens elsewhere in the project.
# When main.py does "from config import *", this code executes first,
# so by the time loader.py or split_speakers.py imports pydub, ffmpeg is already in PATH.
FFMPEG_BIN_PATH = os.path.join(BIN_DIR, "ffmpeg")

if os.path.exists(FFMPEG_BIN_PATH):
    os.environ["PATH"] = FFMPEG_BIN_PATH + os.pathsep + os.environ.get("PATH", "")

# Application Paths
INPUT_FILE = os.path.join(DATA_FOLDER, "input", "sample.wav")
CLEAN_AUDIO_FILE = os.path.join(DATA_FOLDER, "input", "clean_audio.wav")
OUTPUT_FOLDER = os.path.join(DATA_FOLDER, "output")
OUTPUT_VISUALS = DATA_FOLDER
SAMPLE_RATE = 64000