import os
import json

from config import *

from audio_processing.loader import load_audio
from audio_processing.noise_cleaner import clean_noise

from diarization.diarize import perform_diarization

from utils.timestamps import group_by_speaker

from separation.split_speakers import split_into_speakers

from visualization import create_all_visualizations
from GUI.fileExplorer import launch_data_explorer


def main():

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print("Loading audio...")

    load_audio(INPUT_FILE, CLEAN_AUDIO_FILE)

    print("Cleaning noise...")

    clean_noise(CLEAN_AUDIO_FILE, CLEAN_AUDIO_FILE)

    print("Running speaker diarization...")

    segments = perform_diarization(CLEAN_AUDIO_FILE)

    print("Grouping speakers...")

    speakers = group_by_speaker(segments)

    print("Splitting speakers...")

    split_into_speakers(
        CLEAN_AUDIO_FILE,
        speakers,
        OUTPUT_FOLDER
    )
    print("Done!")
    print(f"Speakers detected: {len(speakers)}")
    
    segments_file = os.path.join(OUTPUT_FOLDER, "segments.json")
    with open(segments_file, "w") as f:
        json.dump(segments, f, indent=4)
    
    create_all_visualizations(CLEAN_AUDIO_FILE, segments, OUTPUT_VISUALS, OUTPUT_FOLDER)
    launch_data_explorer(DATA_FOLDER)
    


if __name__ == "__main__":
    main()
