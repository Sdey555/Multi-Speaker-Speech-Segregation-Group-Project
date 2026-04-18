# Multi-Speaker Speech Segregation

A Python-based system for **multi-speaker speech segregation** that takes a mixed audio recording and separates it into speaker-wise outputs. The project combines audio preprocessing, pretrained speaker diarization, custom post-processing, and visualization to make the results easier to interpret.

## Features

* Converts input audio to mono WAV format
* Applies noise reduction before diarization
* Uses pretrained speaker diarization models
* Refines raw diarization output with custom post-processing
* Exports speaker-wise audio files
* Saves diarization output as JSON
* Generates waveform, spectrogram, and speaker timeline visualizations
* Includes a GUI-based data explorer and interactive speaker timeline
* Portable FFmpeg setup bundled with the repository

## How It Works

```text
Input Audio
→ Mono Conversion
→ Noise Reduction
→ Speaker Diarization
→ Post-processing
→ Speaker Grouping
→ Audio Splitting
→ Visualization
→ GUI Data Explorer
→ Output
```

## Project Structure

```text
Multi-Speaker-Speech-Segregation-Group-Project/
|-- audio_processing/
|   |-- loader.py
|   `-- noise_cleaner.py
|-- bin/
|   `-- ffmpeg/
|       |-- ffmpeg.exe
|       `-- ffprobe.exe
|-- diarization/
|   `-- diarize.py
|-- GUI/
|   |-- fileExplorer.py
|   `-- timeline_ui.py
|-- separation/
|   `-- split_speakers.py
|-- utils/
|   `-- timestamps.py
|-- visualization/
|   |-- __init__.py
|   `-- plots.py
|-- Data/
|   |-- input/
|   |-- output/
|   `-- visualizations/
|-- config.py
|-- main.py
|-- requirements.txt
|-- setup_env.bat
`-- README.md
```

## Requirements

### System Requirements

* Windows PowerShell
* Python 3.11 or newer
* FFmpeg binaries placed in `bin/ffmpeg/`
* A Hugging Face account and access token
* Enough disk space for model downloads and generated output

### Python Dependencies

Install the required packages with:

```bash
pip install -r requirements.txt
```

Main libraries used:

* `pyannote.audio`
* `torch`
* `torchaudio`
* `librosa`
* `pydub`
* `noisereduce`
* `numpy`
* `matplotlib`
* `soundfile`
* `PySide6`

## Hugging Face Setup

This project uses pretrained diarization models from Hugging Face.

Before running the project:

1. Create a Hugging Face account at [https://huggingface.co/](https://huggingface.co/)
2. Accept the access conditions for the required `pyannote` model repositories
3. Log in locally so the model files can be downloaded

Login command:

```bash
hf auth login
```

## How to Run

1. Choose an input audio file from the GUI or place it in:

```text
Data/input/
```

2. Make sure FFmpeg binaries are present in:

```text
bin/ffmpeg/
```

3. Run the project:

```bash
python main.py
```

4. Use the GUI to select the input file and run the pipeline without terminal interaction.

## Output

After execution, the project generates:

```text
Data/output/
├── speaker-wise WAV files
├── segments.json
```

And visualizations in:

```text
Data/visualizations/
├── waveform.png
├── spectrogram.png
├── speaker_timeline.png
├── speaker-wise waveform images
└── speaker-wise spectrogram images
```

The GUI data explorer also opens to help browse and preview the generated files.

## Visualization

The visualization module creates graphical representations of the processed audio and diarization results.

### Generated Visuals

* **Waveform** — amplitude vs. time
* **Spectrogram** — frequency content vs. time
* **Speaker Timeline** — speaker activity over time

If speaker-wise audio is available, the system also generates:

* speaker waveform plots
* speaker spectrogram plots

These visuals help interpret the diarization output and inspect speaker separation quality.

## Post-processing

The raw diarization output is refined using:

* Segment normalization
* Merging adjacent segments of the same speaker
* Bridging short interruptions
* Removing tiny segments that are likely noise

This improves the readability and stability of the final segmentation.

## GUI Features

The project includes a GUI-based data explorer that can:

* browse generated files
* preview images
* play speaker audio files
* open an interactive speaker timeline

This makes the project easier to demo and inspect.

## Limitations

* Performance depends on audio quality
* Similar-sounding speakers may be merged incorrectly
* Overlapping speech is still challenging
* Very short segments may be affected by post-processing
* Diarization accuracy can vary across different recordings

## Future Improvements

* Better overlap handling
* Improved speaker counting and clustering
* Real-time processing
* Cleaner UI/UX for the data explorer
* More detailed analytics for speaker segmentation

## References

* Pyannote Audio: [https://github.com/pyannote/pyannote-audio](https://github.com/pyannote/pyannote-audio)
* Hugging Face: [https://huggingface.co/](https://huggingface.co/)
* Librosa: [https://librosa.org/](https://librosa.org/)
* PyTorch: [https://pytorch.org/](https://pytorch.org/)
* Pydub: [https://github.com/jiaaro/pydub](https://github.com/jiaaro/pydub)
* noisereduce: [https://github.com/timsainb/noisereduce](https://github.com/timsainb/noisereduce)
* PySide6: [https://doc.qt.io/qtforpython/](https://doc.qt.io/qtforpython/)

## Summary

This project demonstrates how machine learning and signal processing can be combined to build a complete pipeline for multi-speaker speech segregation, making complex audio data structured, interpretable, and easier to analyze.
