# Multi‑Speaker Speech Segregation

A **Python‑based** pipeline that takes a mixed‑audio recording and separates it into **speaker‑wise** output files. The system combines audio preprocessing, pretrained speaker diarization, custom post‑processing, and rich visualizations, all wrapped in an interactive GUI data explorer.

---

## ✨ Features

- **Multi‑Mode Segregation**:
  - **Speaker Diarization**: Separate multiple voices using `pyannote.audio`.
  - **Speaking vs. Singing**: Distinguish between speech and singing using `ced-tiny`.
  - **Instrument Sounds**: Identify and segregate specific instrument sounds (Violin, Sitar, etc.).
- **Mono conversion** and **noise reduction** before processing.
- Robust post‑processing: segment normalization, merging, bridging short gaps, and filtering tiny noisy segments.
- Automatic **segmented audio extraction** and JSON export of metadata.
- High‑quality visualizations:
  - Waveform & spectrogram of the whole recording.
  - Interactive segment timeline with playback.
  - Per‑segment waveform & spectrogram images.
- **GUI data explorer** (PySide6) with one-click mode switching and automatic folder cleanup.
- Portable **FFmpeg** binaries bundled in the repository for seamless audio handling on Windows.

---

## 📁 Project Structure

```text
Multi-Speaker-Speech-Segregation-Group-Project/
├─ audio_processing/          # Loader & noise‑reduction utilities
│   ├─ loader.py
│   └─ noise_cleaner.py
├─ bin/ffmpeg/                # FFmpeg executables (ffmpeg.exe, ffprobe.exe)
├─ diarization/               # Core segregation scripts
│   ├─ diarize.py             # Speaker diarization logic
│   └─ sound_classifier.py    # CED-Tiny multi-mode classification
├─ GUI/                       # Interactive data explorer & timeline UI
│   ├─ app.py
│   ├─ fileExplorer.py
│   └─ timeline_ui.py
├─ separation/                # Speaker‑wise audio splitting
│   └─ split_speakers.py
├─ utils/                     # Helper utilities (timestamps, etc.)
│   └─ timestamps.py
├─ visualization/             # Plotting utilities
│   ├─ __init__.py
│   └─ plots.py
├─ Data/                      # Sample input / generated output
│   ├─ input/
│   ├─ output/
│   └─ visualizations/
├─ config.py                  # Global configuration (paths, constants)
├─ main.py                    # Entry‑point that launches the GUI
├─ requirements.txt           # Exact Python dependencies (pinned versions)
├─ setup_env.bat              # Convenience script to create venv & install deps
├─ start.bat                  # Shortcut to activate venv and run the app
└─ README.md                  # **You are reading it!**
```

---

## 📦 Requirements

### System
- Windows 10/11 (PowerShell) – the project is tested on Windows.
- **Python 3.11+** (the `setup_env.bat` script creates a virtual environment).
- FFmpeg binaries placed in `bin/ffmpeg/` (included in the repo).
- A Hugging Face account with access to the required `pyannote` model repositories.

### Python Packages
The exact versions are pinned in `requirements.txt`:

```text
pyannote.audio==4.0.4
torch==2.11.0
torchaudio==2.11.0
transformers>=4.40.0
tokenizers>=0.20.0
librosa==0.11.0
pydub==0.25.1
noisereduce==3.0.3
numpy==2.4.4
matplotlib==3.10.8
soundfile==0.13.1
PySide6==6.10.1
huggingface-hub>=0.20.0
regex
```

Install them with:

```bash
pip install -r requirements.txt
```

---

## 🔑 Hugging Face Setup

1. Create a Hugging Face account at <https://huggingface.co/>.
2. Accept the access conditions for the `pyannote` model repositories you intend to use.
3. Log in locally so the model files can be downloaded:

```bash
hf auth login
```

---

## 🚀 How to Run

1. **Place your input audio** (any format supported by FFmpeg) in `Data/input/`.
2. Verify that the FFmpeg binaries exist in `bin/ffmpeg/`.
3. Activate the virtual environment and launch the GUI:

```bash
# Using the provided batch shortcut
start.bat

# Or double‑click the Windows script to launch the batch file
run_voice_segregator.vbs
```

   *or* manually:

```bash
call venv\Scripts\activate
python main.py
```

4. In the GUI, select the input file and click **Run**. The pipeline will process the audio, generate speaker‑wise files, JSON metadata, and visualizations.

---

## 📂 Output

After a successful run you will find:

```text
Data/output/
├─ speaker_01.wav
├─ speaker_02.wav
├─ ...
└─ segments.json          # diarization metadata (start, end, speaker ID)
```

Visualizations are saved under `Data/visualizations/`:

```text
Data/visualizations/
├─ waveform.png
├─ spectrogram.png
├─ speaker_timeline.png
├─ speaker_01_waveform.png
├─ speaker_01_spectrogram.png
└─ ...
```

The GUI data explorer also opens automatically, allowing you to preview and play any generated file.

---

## 🛠️ Post‑Processing Details

The raw diarization output is refined using the following steps:

- **Segment Normalization** – ensures consistent start/end timestamps.
- **Merging** – adjacent segments belonging to the same speaker are merged.
- **Bridging** – short pauses (< 200 ms) between the same speaker are bridged.
- **Filtering** – removes tiny segments (< 300 ms) that are likely noise.

These heuristics improve readability and stability of the final speaker segmentation.

---

## 🎨 GUI Features

- **File Explorer** – browse `Data/` folders, preview images, and play audio.
- **Interactive Speaker Timeline** – click on any segment to hear the corresponding speaker audio.
- **Real‑time Progress** – visual feedback while the pipeline runs.

---

## ⚠️ Limitations

- Accuracy depends on the quality of the input recording.
- Very similar‑sounding speakers may be merged incorrectly.
- Overlapping speech remains challenging for the current diarization model.
- Extremely short segments may be removed during post‑processing.

---

## 🔮 Future Improvements

- Enhanced handling of overlapping speech.
- More sophisticated speaker counting and clustering algorithms.
- Real‑time processing mode.
- Refined UI/UX for the data explorer (dark mode, theming).
- Detailed analytics dashboard for speaker statistics.

---

## 📚 References

- **pyannote.audio** – <https://github.com/pyannote/pyannote-audio>
- **Hugging Face** – <https://huggingface.co/>
- **Librosa** – <https://librosa.org/>
- **PyTorch** – <https://pytorch.org/>
- **pydub** – <https://github.com/jiaaro/pydub>
- **noisereduce** – <https://github.com/timsainb/noisereduce>
- **PySide6** – <https://doc.qt.io/qtforpython/>

---

## 📖 Summary

This project demonstrates how modern machine‑learning models and classic signal‑processing techniques can be combined to build a complete, end‑to‑end pipeline for **multi‑speaker speech segregation**. It provides a user‑friendly GUI, high‑quality visualizations, and a reproducible workflow that can be extended for research or production use.
