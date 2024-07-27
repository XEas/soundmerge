import random
import numpy as np
import logging
from typing import Union, Iterable
from pathlib import Path
from pydub import AudioSegment
from augm import mix_overlay, random_segment, concatenate
from uniform import get_percentile_dBFS, normalize_dBFS
from loguru import logger

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pathLike = Union[str, Path]

def random_coefficient() -> float:
    """
    Generates a random coefficient between 0 and 1
    """
    return random.random()

def choose_volume(coefs : list, distr: str) -> float:
    """
    Chooses volume so the distribution of the coefficients is uniform or normal, as specified
    """
    coefs = [value for value in coefs if value > -np.inf]
    if distr == 'uniform':
        return random.choice(coefs)
    elif distr == 'normal':
        return np.average(np.array(coefs))
    
    raise ValueError("Distribution type must be 'uniform' or 'normal'") 

def choose_audio(path : Path):
    """
    Chooses a random audio file from the given directory
    """
    audio_files = [file for file in path.glob('*.wav') if not file.name.startswith('._')] #ignore hidden files
    if audio_files:
        return random.choice(audio_files)
    return None

def calculate_db_loss(percent : float) -> float:
    """
    Calculates the dB loss from the given percentage.
    """
    if not 0 <= percent <= 1:
        raise ValueError("Percent must be between 0 and 1.")
    if percent == 0:
        raise ValueError("Percent of 0 indicates infinite dB loss, which is not representable.")
    elif percent == 1:
        return 0
    return -10 * np.log10(percent)

@logger.catch
def dynamic_select_benchmark(audio_file_count : int, destination_directory: Path, source_directories: Iterable[Path], percentiles: Iterable[float], distribution : str, duration: float):
    """
    Creates a testing benchmark with the given number of audio files, multiple directories, percentiles, distribution type
    """
    percentile_norms = [get_percentile_dBFS(path=dir, percentile=percentile) for dir, percentile in zip(source_directories, percentiles)]

    duration_ms = int(duration * 1000)
    for i in range(audio_file_count):
        logger.info(f"Audio #{i+1} generation started")
        # choose audio files from each directory to mix
        segments_to_mix = []
        for j, path in enumerate(source_directories):
            chosen_audio_path = choose_audio(path=path)
            logger.info(f"Chosen audio: {chosen_audio_path.name}")
            segment = normalize_dBFS(path=chosen_audio_path, target_dBFS=percentile_norms[j])
            segments_to_mix.append(segment)

        # mix chosen audio files
        # literally a canvas to put audio on
        canvas = AudioSegment.silent(duration=duration_ms)
        for j, path in enumerate(source_directories):
            segment = segments_to_mix[j]
            if len(segment) > duration_ms:
                segment = random_segment(audio_segment=segment, length_ms=duration_ms)
            while len(segment) < duration_ms:
                extra_chosen_audio_path = choose_audio(path)
                extra_segment = normalize_dBFS(path=extra_chosen_audio_path, target_dBFS=percentile_norms[j])
                segment = concatenate(audio_segment1=segment, audio_segment2=extra_segment, crossfade_duration=100)

            sc = random_coefficient()
            segment = segment - calculate_db_loss(sc)
            logger.info(f"Segment {j+1} coefficient: {sc} Volume: {segment.dBFS} dBFS")

            mixed_segment = mix_overlay(canvas, segment)

            chosen_volume = choose_volume(coefs=[canvas.dBFS, segment.dBFS], distr=distribution)
            mixed_segment = mixed_segment.apply_gain(volume_change=(chosen_volume - mixed_segment.dBFS))
            
            canvas = mixed_segment
            
        logger.info(f"Final volume: {canvas.dBFS} dBFS")
        mixed_segment.export(destination_directory / f"audio{i+1}.wav", format='wav')