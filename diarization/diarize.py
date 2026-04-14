from pyannote.audio import Pipeline
import soundfile as sf
import torch


MIN_SEGMENT_DURATION = 0.45
MERGE_GAP_SECONDS = 0.6
MAX_BRIDGED_INTERRUPT_SECONDS = 0.8
EXPECTED_SPEAKERS = 2


def _normalize_segments(segments):
    normalized = []

    for seg in sorted(segments, key=lambda item: item["start"]):
        start = max(0.0, float(seg["start"]))
        end = max(start, float(seg["end"]))

        if end - start <= 0.0:
            continue

        normalized.append({
            "start": start,
            "end": end,
            "speaker": seg["speaker"]
        })

    return normalized


def _merge_same_speaker_segments(segments, max_gap=MERGE_GAP_SECONDS):
    merged = []

    for seg in segments:
        if not merged:
            merged.append(seg.copy())
            continue

        last = merged[-1]
        gap = seg["start"] - last["end"]

        if seg["speaker"] == last["speaker"] and gap <= max_gap:
            last["end"] = max(last["end"], seg["end"])
        else:
            merged.append(seg.copy())

    return merged


def _bridge_short_interruptions(segments, max_interrupt=MAX_BRIDGED_INTERRUPT_SECONDS):
    if len(segments) < 3:
        return segments

    bridged = []
    index = 0

    while index < len(segments):
        current = segments[index].copy()

        if 0 < index < len(segments) - 1:
            previous = bridged[-1] if bridged else None
            following = segments[index + 1]
            duration = current["end"] - current["start"]

            if (
                previous
                and previous["speaker"] == following["speaker"]
                and current["speaker"] != previous["speaker"]
                and duration <= max_interrupt
                and current["start"] - previous["end"] <= MERGE_GAP_SECONDS
                and following["start"] - current["end"] <= MERGE_GAP_SECONDS
            ):
                previous["end"] = max(previous["end"], following["end"])
                index += 2
                continue

        bridged.append(current)
        index += 1

    return bridged


def _drop_tiny_segments(segments, min_duration=MIN_SEGMENT_DURATION):
    if not segments:
        return segments

    refined = []

    for seg in segments:
        duration = seg["end"] - seg["start"]

        if duration >= min_duration or not refined:
            refined.append(seg.copy())
            continue

        refined[-1]["end"] = max(refined[-1]["end"], seg["end"])

    return refined


def _extract_segments(diarization_output):
    annotation = getattr(diarization_output, "speaker_diarization", diarization_output)
    segments = []

    if hasattr(annotation, "itertracks"):
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            segments.append({
                "start": float(turn.start),
                "end": float(turn.end),
                "speaker": speaker
            })
        return segments

    for item in annotation:
        if len(item) == 3:
            turn, _, speaker = item
        else:
            turn, speaker = item

        segments.append({
            "start": float(turn.start),
            "end": float(turn.end),
            "speaker": speaker
        })

    return segments


def perform_diarization(audio_file, expected_speakers=EXPECTED_SPEAKERS):
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

    diarization = pipeline(audio_data, num_speakers=expected_speakers)
    segments = _extract_segments(diarization)

    segments = _normalize_segments(segments)
    segments = _merge_same_speaker_segments(segments)
    segments = _bridge_short_interruptions(segments)
    segments = _merge_same_speaker_segments(segments)
    segments = _drop_tiny_segments(segments)
    segments = _merge_same_speaker_segments(segments)

    return segments
