import librosa
import numpy as np
from transformers import pipeline

def normalize_label(label: str) -> str:
    """Clean label to be safe for filenames."""
    return label.replace(" ", "_").replace(",", "").replace("/", "_").replace("\\", "_")

def perform_sound_classification(audio_file, mode_type="vocals"):
    """
    mode_type: 
        'vocals' for Speech vs Singing segregation
        'instruments' for specific instrument sound segregation
    """
    print(f"Loading CED-Tiny model for '{mode_type}' mode...")
    classifier = pipeline("audio-classification", model="mispeech/ced-tiny", trust_remote_code=True)
    
    print("Loading audio for classification...")
    # Load audio at 16kHz (standard for CED models)
    y, sr = librosa.load(audio_file, sr=16000)
    
    chunk_duration = 2.0  # seconds per inference chunk
    step_duration = 1.0   # seconds overlap (sliding window)
    chunk_samples = int(chunk_duration * sr)
    step_samples = int(step_duration * sr)
    
    segments = []
    total_samples = len(y)
    
    print("Classifying audio segments...")
    for start_sample in range(0, total_samples, step_samples):
        end_sample = min(start_sample + chunk_samples, total_samples)
        
        chunk = y[start_sample:end_sample]
        
        if len(chunk) < sr * 0.2:
            break
            
        preds = classifier(chunk)
        if not preds: 
            continue
            
        top_pred = preds[0]['label']
        
        final_label = None
        
        if mode_type == "vocals":
            if any(x in top_pred for x in ["Speech", "Conversation", "Narration", "Speech synthesizer"]):
                final_label = "Speech"
            elif any(x in top_pred for x in ["Singing", "Music", "Song"]):
                final_label = "Singing_or_Music"
                
        elif mode_type == "instruments":
            # Ignore primary vocals/silence/noise, keep pure instruments
            ignored_common = ["Speech", "Silence", "Noise", "Singing", "Breathing", "Inside", "Outside"]
            if not any(ign in top_pred for ign in ignored_common):
                final_label = top_pred
                
        if final_label:
            final_label = normalize_label(final_label)
            start_time = float(start_sample / sr)
            end_time = float(end_sample / sr)
            segments.append({
                "start": start_time,
                "end": end_time,
                "speaker": final_label  # we use "speaker" key to fit the existing pipeline
            })
            
    # Merge overlapping/adjacent segments of the same type
    print("Merging contiguous segments...")
    merged_segments = []
    for seg in segments:
        if not merged_segments:
            merged_segments.append(seg.copy())
            continue
            
        last = merged_segments[-1]
        
        # If the same category and gap is small (<= 1.5 seconds)
        if seg["speaker"] == last["speaker"] and (seg["start"] - last["end"] <= 1.5):
            last["end"] = max(last["end"], seg["end"])
        else:
            merged_segments.append(seg.copy())
            
    return merged_segments
