# Multi-Speaker-Speech-Segregation

Multi-Speaker-Speech-Segregation is a Python project that:

- converts an input audio file to mono WAV
- applies noise reduction
- runs speaker diarization with `pyannote.audio`
- groups diarized segments by speaker
- exports one WAV file per detected speaker
- shows a waveform preview of the processed audio

This project is designed for local use and currently assumes a two-speaker diarization workflow.

## Features

- automatic audio conversion to WAV
- noise cleaning before diarization
- speaker diarization using `pyannote/speaker-diarization-3.1`
- speaker-wise audio export
- simple pipeline entry point through `main.py`
- waveform, spectrogram, and speaker timeline visualization

## Project Structure

```text
DemoSpeakerSplitter/
|-- audio_processing/
|   |-- loader.py
|   `-- noise_cleaner.py
|-- diarization/
|   `-- diarize.py
|-- separation/
|   `-- split_speakers.py
|-- utils/
|   |-- timestamps.py
|   `-- visualization.py
|-- visualization/
|   |-- __init__.py
|   `-- plots.py
|-- input/
|-- output/
|-- config.py
|-- main.py
|-- requirements.txt
`-- README.md
```

## Requirements

Recommended environment:

- Windows PowerShell
- Python 3.11 or newer
- `ffmpeg` installed and available in `PATH`
- a Hugging Face account and access token

## Python Dependencies

The project uses these direct dependency versions:

```text
pyannote.audio==4.0.4
torch==2.11.0
torchaudio==2.11.0
librosa==0.11.0
pydub==0.25.1
noisereduce==3.0.3
numpy==2.4.4
matplotlib==3.10.8
soundfile==0.13.1
```

Install them with:

```powershell
pip install -r requirements.txt
```

## External Dependencies

### FFmpeg

`pydub` depends on FFmpeg for reliable audio handling.

Install FFmpeg on Windows and make sure `ffmpeg` is available in your `PATH`.

To verify:

```powershell
ffmpeg -version
```

### Hugging Face Access

This project requires Hugging Face because it loads the pretrained diarization pipeline:

```text
pyannote/speaker-diarization-3.1
```

Before running the project:

1. Create a Hugging Face account at `https://huggingface.co/`
2. Accept the model access conditions for `pyannote/speaker-diarization-3.1`
3. Generate a Hugging Face access token
4. Log in locally so `pyannote.audio` can download the model

You can log in with:

```powershell
huggingface-cli login
```

When prompted, paste your token.

## Installation

### 1. Clone the repository

```powershell
git clone <your-repo-url>
cd DemoSpeakerSplitter
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Install and verify FFmpeg

```powershell
ffmpeg -version
```

### 5. Authenticate with Hugging Face

```powershell
huggingface-cli login
```

## Input and Output

Default paths are defined in [config.py](/e:/Projects/DemoSpeakerSplitter/config.py:1):

```python
INPUT_FILE = "input/sound.wav"
CLEAN_AUDIO_FILE = "input/clean_audio.wav"
OUTPUT_FOLDER = "output"
SAMPLE_RATE = 64000
```

What this means:

- place your source audio at `input/sound.wav`
- the cleaned intermediate file will be written to `input/clean_audio.wav`
- separated speaker tracks will be written into `output/`

## How to Run

After setup, run:

```powershell
python main.py
```

Pipeline steps:

1. Load the input audio
2. Convert it to mono WAV
3. Clean background noise
4. Run speaker diarization
5. Group timestamp segments per speaker
6. Export one WAV file per speaker
7. Generate waveform, spectrogram, and speaker timeline visualizations

## Example Output

After a successful run, you should see files similar to:

```text
output/SPEAKER_00.wav
output/SPEAKER_01.wav
```

The exact speaker labels may vary depending on the diarization result.

## Visualization

The project includes a visualization module that generates graphical representations of the processed audio and diarization results. These visualizations help interpret how the system identifies and separates speakers over time.
Types of Visualizations

1. Waveform
  - Displays amplitude of the audio signal over time
  - Helps identify speech regions and silence
  - Useful for understanding overall audio structure
2. Spectrogram
  - Shows frequency distribution over time
  - Highlights speech patterns and energy levels
  - Useful for analyzing acoustic characteristics
3. Speaker Timeline
  - Visual representation of speaker activity
  - Each speaker is shown with a different color
  - Clearly indicates who spoke when
# Implementation
  - The visualization logic is implemented in the visualization/ module.
# Main Function:
  ```
   create_all_visualizations(audio_file, segments, output_folder)
  ```
This function generates all visual outputs in a single step.
# Output Location
  All visualizations are saved in:
  ```text
    output/visualizations/
  ├── waveform.png
  ├── spectrogram.png
  └── speaker_timeline.png
  ```
# Purpose
 - Visualization improves interpretability of the diarization process by:
  - making speaker transitions easy to understand
  - validating segmentation quality
  - providing visual insight into audio processing

## Notes and Limitations

- the project currently works best for two-speaker audio
- overlap, crosstalk, background music, and poor microphone quality can reduce separation quality
- longer recordings may take more time because the diarization model runs locally
- a warning about `torchcodec` may appear in some environments; this project passes audio in memory, so that warning does not necessarily block execution
- the Hugging Face model must be accessible from your account before first run

## Troubleshooting

### Hugging Face model download fails

Make sure:

- you are logged in with `huggingface-cli login`
- your token is valid
- you accepted the access terms for `pyannote/speaker-diarization-3.1`

### FFmpeg is not found

Install FFmpeg and confirm:

```powershell
ffmpeg -version
```

### No separated speaker files are created

Check:

- the input file exists at `input/sound.wav`
- the audio is valid and not empty
- the Hugging Face model downloaded successfully
- the console output for diarization errors

### Speaker separation quality is weak

This can happen when:

- both speakers sound very similar
- speakers interrupt each other often
- the recording has heavy background noise
- the input audio is very compressed or low quality

## Usage Summary

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
huggingface-cli login
python main.py
```

## License

Add a license file if you plan to share or publish this repository publicly.
