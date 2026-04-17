import librosa
import noisereduce as nr
import soundfile as sf

def clean_noise(input_wav, output_wav):

    audio, sr = librosa.load(input_wav, sr=None)

    reduced = nr.reduce_noise(
        y=audio,
        sr=sr
    )

    sf.write(output_wav, reduced, sr)

    print("Noise reduction complete.")