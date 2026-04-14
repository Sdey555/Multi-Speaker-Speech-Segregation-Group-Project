from pydub import AudioSegment
import os

def split_into_speakers(audio_file, speakers, output_folder):

    audio = AudioSegment.from_wav(audio_file)

    duration = len(audio)

    for speaker in speakers:

        speaker_audio = AudioSegment.silent(duration=duration)

        for start, end in speakers[speaker]:

            start_ms = int(start * 1000)
            end_ms = int(end * 1000)

            segment = audio[start_ms:end_ms]

            speaker_audio = speaker_audio.overlay(segment, position=start_ms)

        output_path = os.path.join(output_folder, f"{speaker}.wav")

        speaker_audio.export(output_path, format="wav")

        print(f"Saved {output_path}")