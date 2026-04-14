def group_by_speaker(segments):
    speakers = {}
    for seg in segments:
        sp = seg["speaker"]
        if sp not in speakers:
            speakers[sp] = []
        speakers[sp].append((seg["start"], seg["end"]))
    return speakers