from pydub import AudioSegment
import os

BOUNDARY_PADDING_MS = 120
PAUSE_DURATION_MS = 2000  # 2 seconds pause between non-consecutive segments


def split_into_speakers(audio_file, speakers, output_folder):

    audio = AudioSegment.from_wav(audio_file)

    for speaker in speakers:

        # Sort segments by start time (should already be sorted, but ensure it)
        segments = sorted(speakers[speaker], key=lambda x: x[0])

        # Create concatenated audio with pauses between non-consecutive segments
        speaker_audio_parts = []

        for i, (start, end) in enumerate(segments):
            start_ms = max(0, int(start * 1000) - BOUNDARY_PADDING_MS)
            end_ms = min(len(audio), int(end * 1000) + BOUNDARY_PADDING_MS)

            if end_ms <= start_ms:
                continue

            segment = audio[start_ms:end_ms]
            speaker_audio_parts.append(segment)

            # Add pause after each segment except the last one
            if i < len(segments) - 1:
                speaker_audio_parts.append(AudioSegment.silent(duration=PAUSE_DURATION_MS))

        # Concatenate all parts
        if speaker_audio_parts:
            speaker_audio = sum(speaker_audio_parts[1:], speaker_audio_parts[0]) if len(speaker_audio_parts) > 1 else speaker_audio_parts[0]
        else:
            speaker_audio = AudioSegment.silent(duration=1000)  # 1 second silent if no segments

        output_path = os.path.join(output_folder, f"{speaker}.wav")

        speaker_audio.export(output_path, format="wav")

        print(f"Saved {output_path}")
