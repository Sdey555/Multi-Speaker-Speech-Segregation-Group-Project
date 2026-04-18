import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def plot_waveform(audio_file: str, save_path: str):
    y, sr = librosa.load(audio_file, sr=None)

    plt.figure(figsize=(14, 4))
    librosa.display.waveshow(y, sr=sr)
    plt.title("Cleaned Audio Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def plot_spectrogram(audio_file: str, save_path: str):
    y, sr = librosa.load(audio_file, sr=None)

    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)

    plt.figure(figsize=(14, 5))
    librosa.display.specshow(D, sr=sr, x_axis="time", y_axis="hz")
    plt.colorbar(format="%+2.0f dB")
    plt.title("Spectrogram")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def plot_speaker_timeline(segments, save_path: str):
    """
    segments format:
    [
        {"start": 0.0, "end": 2.3, "speaker": "SPEAKER_00"},
        ...
    ]
    """
    if not segments:
        return

    speakers = sorted(list(set(seg["speaker"] for seg in segments)))
    speaker_to_y = {spk: i for i, spk in enumerate(speakers)}

    plt.figure(figsize=(14, max(3, len(speakers) * 0.6)))

    colors = plt.cm.tab10.colors

    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        speaker = seg["speaker"]
        y = speaker_to_y[speaker]

        plt.barh(
            y=y,
            width=end - start,
            left=start,
            height=0.35,
            color=colors[y % len(colors)],
            edgecolor="black",
            alpha=0.85
        )

        plt.text(
            (start + end) / 2,
            y,
            speaker,
            ha="center",
            va="center",
            color="white",
            fontsize=9,
            fontweight="bold"
        )

    plt.yticks(range(len(speakers)), speakers)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Speaker")
    plt.title("Speaker Timeline")
    plt.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def create_all_visualizations(audio_file: str, segments, output_folder: str, speaker_audio_folder: str = None):
    vis_dir = os.path.join(output_folder, "visualizations")
    _ensure_dir(vis_dir)

    plot_waveform(audio_file, os.path.join(vis_dir, "waveform.png"))
    plot_spectrogram(audio_file, os.path.join(vis_dir, "spectrogram.png"))
    plot_speaker_timeline(segments, os.path.join(vis_dir, "speaker_timeline.png"))

    if speaker_audio_folder:
        for file in os.listdir(speaker_audio_folder):
            if file.endswith(".wav"):
                spk = os.path.splitext(file)[0]
                spk_audio = os.path.join(speaker_audio_folder, file)
                plot_waveform(spk_audio, os.path.join(vis_dir, f"{spk}_waveform.png"))
                plot_spectrogram(spk_audio, os.path.join(vis_dir, f"{spk}_spectrogram.png"))

    print(f"Visualizations saved in: {vis_dir}")