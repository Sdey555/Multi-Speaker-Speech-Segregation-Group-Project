MERGE_GAP_SECONDS = 0.35


def group_by_speaker(segments):
    speakers = {}

    for seg in segments:
        speaker = seg["speaker"]
        speakers.setdefault(speaker, []).append((seg["start"], seg["end"]))

    for speaker, intervals in speakers.items():
        merged = []

        for start, end in sorted(intervals):
            if not merged:
                merged.append([start, end])
                continue

            last_start, last_end = merged[-1]

            if start - last_end <= MERGE_GAP_SECONDS:
                merged[-1][1] = max(last_end, end)
            else:
                merged.append([start, end])

        speakers[speaker] = [(start, end) for start, end in merged]

    return speakers
