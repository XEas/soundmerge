"""Intended to create a directory of sound files with uniform loudness."""
from pydub import AudioSegment
import os
from pathlib import Path
from loguru import logger

def get_median_dBFS(path : Path) -> float:
    """Calculates the median dBFS value of all .wav files in the given directory."""
    dBFS_values = []
    for filename in path.iterdir():
        if filename.suffix != ".wav" or filename.name.startswith('._'):
            continue
        audio = AudioSegment.from_file(str(path / filename), format="wav")
        dBFS_values.append(audio.dBFS)
    
    median = sorted(dBFS_values)[len(dBFS_values) // 2]
    
    return median

def get_percentile_dBFS(paths: list[Path], percentile: float) -> float:
    """Calculates the specified quantile dBFS value of all .wav files in the given list."""
    dBFS_values = [AudioSegment.from_file(str(path), format="wav").dBFS for path in paths if path.suffix == ".wav" and not path.name.startswith('._')]
    
    index = int(len(dBFS_values) * percentile)
    index = max(min(index, len(dBFS_values) - 1), 0)
    
    percentile_value = sorted(dBFS_values)[index]
    
    logger.info(f"Percentile dBFS value: {percentile_value}")

    return percentile_value

def normalize_dBFS(path: Path, target_dBFS: float, **kwargs) -> AudioSegment:
    audio = AudioSegment.from_file(path, format="wav")
    audio = audio.apply_gain(target_dBFS - audio.dBFS)
    
    return audio

def normalize_segment_dBFS(segment: AudioSegment, target_dBFS: float, **kwargs) -> AudioSegment:
    audio = segment.apply_gain(target_dBFS - segment.dBFS)
    return audio