@echo off
setlocal

echo [1/3] Creating Virtual Environment...
python -m venv venv

echo [2/3] Activating Environment and Installing Dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

echo [3/3] Verifying Setup...
if exist bin\ffmpeg\ffmpeg.exe (
    echo [SUCCESS] FFmpeg found in bin/ffmpeg/
) else (
    echo [WARNING] FFmpeg binaries not found in bin/ffmpeg/. 
    echo Please download ffmpeg.exe and ffprobe.exe and place them in the bin/ffmpeg folder.
)

echo Setup Complete! To run the application, use:
echo call venv\Scripts\activate
echo python main.py
pause
