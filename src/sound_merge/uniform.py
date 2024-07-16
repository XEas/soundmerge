"""Intended to create a directory of sound files with uniform loudness."""
from pydub import AudioSegment
import os

def get_median_dBFS(path):
    """Calculates the median dBFS value of all .wav files in the given directory."""
    dBFS_values = []
    for filename in path.iterdir():
        if filename.suffix != ".wav":
            continue
        audio = AudioSegment.from_file(str(path / filename), format="wav")
        dBFS_values.append(audio.dBFS)
    
    median = sorted(dBFS_values)[len(dBFS_values) // 2]
    
    return median

def get_quantile_dBFS(path, quantile):
    """Calculates the specified quantile dBFS value of all .wav files in the given directory."""
    dBFS_values = []
    for filename in path.iterdir():
        if filename.suffix != ".wav":
            continue
        audio = AudioSegment.from_file(str(path / filename), format="wav")
        dBFS_values.append(audio.dBFS)
    
    # Calculate the index for the specified quantile
    quantile_index = int(len(dBFS_values) * (quantile / 100))
    quantile_index = min(max(quantile_index, 0), len(dBFS_values) - 1)  # Ensure index is within bounds
    
    return sorted(dBFS_values)[quantile_index]

def normalize_dBFS(path, target_dBFS, new_path):
    os.makedirs(new_path, exist_ok=True)
    """Normalizes all .wav files in the given directory to the target dBFS value."""
    for filename in path.iterdir():
        if filename.suffix != ".wav":
            continue
        audio = AudioSegment.from_file(str(path / filename), format="wav")
        audio = audio.apply_gain(target_dBFS - audio.dBFS)
        filename = filename.stem + "_normalized.wav"
        audio.export(str(new_path / filename), format="wav")

