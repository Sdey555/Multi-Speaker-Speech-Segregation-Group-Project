from pydub import AudioSegment
import os

def load_audio(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1)
    audio.export(output_path, format="wav")
    print("Audio converted to wav.")