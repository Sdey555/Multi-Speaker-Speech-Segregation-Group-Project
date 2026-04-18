# DemoSpeakerSplitter

DemoSpeakerSplitter is a Python project that:

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

## Project Structure

```text
DemoSpeakerSplitter/
|-- audio_processing/
|   |-- loader.py
|   `-- noise_cleaner.py
|-- bin/
|   `-- ffmpeg/             # Bundle ffmpeg.exe and ffprobe.exe here
|-- diarization/
|   `-- diarize.py
|-- separation/
|   `-- split_speakers.py
|-- utils/
|   |-- timestamps.py
|   `-- visualization.py
|-- Data/
|   |-- input/
|   `-- output/
|-- config.py
|-- main.py
|-- requirements.txt
|-- setup_env.bat           # Automated environment setup
`-- README.md

```

## Requirements

Recommended environment:

- Windows PowerShell
- Python 3.11 or newer
- **FFmpeg binaries** (ffmpeg.exe and ffprobe.exe to be downloaded (https://www.gyan.dev/ffmpeg/builds/) and placed in `bin/ffmpeg/` for portability)

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

### FFmpeg (Portable Setup)

This project is configured to use FFmpeg binaries located within the repository for maximum portability across machines.

1.  Download the FFmpeg "essentials" or "full" build for Windows (e.g., from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)).
2.  Extract `ffmpeg.exe` and `ffprobe.exe` from the `bin` folder of the download.
3.  Place both files into the project's `bin/ffmpeg/` folder.

The code in `config.py` will automatically detect and use these binaries.


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
cd Multi-Speaker-Speech-Segregation-Group-Project
```

### 2. Run the automated setup

Instead of manual installation, you can simply run the included batch script:

```powershell
.\setup_env.bat
```

This will:
- Create a virtual environment (`venv`).
- Install all Python dependencies from `requirements.txt`.
- Check if FFmpeg is placed correctly in `bin/ffmpeg/`.

### 3. Authenticate with Hugging Face

```powershell
.\venv\Scripts\activate
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
7. Display the waveform

## Example Output

After a successful run, you should see files similar to:

```text
output/SPEAKER_00.wav
output/SPEAKER_01.wav
```

The exact speaker labels may vary depending on the diarization result.

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
