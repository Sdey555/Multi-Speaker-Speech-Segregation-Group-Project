from pyannote.audio import Pipeline
import soundfile as sf
import torch


def perform_diarization(audio_file):

    waveform, sample_rate = sf.read(audio_file)

    waveform = torch.tensor(waveform).float()

    if waveform.ndim == 1:
        waveform = waveform.unsqueeze(0)
    else:
        waveform = waveform.T

    audio_data = {
        "waveform": waveform,
        "sample_rate": sample_rate
    }

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=True
    )

    diarization = pipeline(audio_data)

    segments = []

    # ---- ORIGINAL LOOP (kept) ----
    for segment, speaker in diarization.speaker_diarization:

        start = float(segment.start)
        end = float(segment.end)

        # ignore extremely tiny segments (noise / breath)
        if end - start < 0.15:
            continue

        segments.append({
            "start": start,
            "end": end,
            "speaker": speaker
        })

    # ---- IMPROVEMENT: merge fragmented segments ----
    merged_segments = []

    for seg in segments:
        if not merged_segments:
            merged_segments.append(seg)
            continue

        last = merged_segments[-1]

        # if same speaker and very close, merge
        if (
            seg["speaker"] == last["speaker"]
            and seg["start"] - last["end"] < 0.25
        ):
            last["end"] = seg["end"]
        else:
            merged_segments.append(seg)

    return merged_segments