import librosa
import librosa.display
import matplotlib.pyplot as plt

def show_waveform(audio_file):
    y, sr = librosa.load(audio_file)
    plt.figure(figsize=(12,4))
    librosa.display.waveshow(y, sr=sr)
    plt.title("Audio Waveform")
    plt.show()