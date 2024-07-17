"""Intended to create a directory of sound files with uniform loudness."""
from pydub import AudioSegment
import os

def get_median_dBFS(path):
    """Calculates the median dBFS value of all .wav files in the given directory."""
    dBFS_values = []
    for filename in path.iterdir():
        if filename.suffix != ".wav" or filename.name.startswith('._'):
            continue
        audio = AudioSegment.from_file(str(path / filename), format="wav")
        dBFS_values.append(audio.dBFS)
    
    median = sorted(dBFS_values)[len(dBFS_values) // 2]
    
    return median


def normalize_dBFS(path, target_dBFS):
        audio = AudioSegment.from_file(str(path), format="wav")
        audio = audio.apply_gain(target_dBFS - audio.dBFS)
        
        return audio

