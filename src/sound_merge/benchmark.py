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

def take_clean_audio(audio_directory : Path) -> list[Path]:
    """
    Cleans the audio files from hidden files
    """
    clean_files = [file for file in audio_directory.glob('*.wav') if not file.name.startswith('._')] # ignore hidden files

    return clean_files

def filter_out_short_audio(audio_files : Path, duration_ms : int) -> list[Path]:
    """
    Filters out audio files that are shorter than the given duration
    """
    filtered = [audio for audio in audio_files if len(AudioSegment.from_file(audio)) >= duration_ms]
    if len(filtered) == 0:
        raise ValueError("No audio files are long enough")
    return filtered

def choose_audio_from_files(audio_files : Iterable[Path]) -> Path:
    """
    Chooses a random audio file from the given files
    """
    if audio_files:
        return random.choice(audio_files)
    return None

def generate_source_audio(source_directories : Iterable[Path]) -> list[Path]:
    """
    Generates source audio files from the given directories - one from each directory
    returns:
    list of paths to the chosen audio files
    """
    files = []
    for directory in source_directories:
        clean_files = take_clean_audio(audio_directory=directory)
        chosen_file = choose_audio_from_files(audio_files=clean_files)
        files.append(chosen_file)
    return files

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
            # somehow filter out short audio files
            chosen_audio_path = choose_audio(path=path)
            segment = random_segment(audio_segment=segment, length_ms=duration_ms)
            logger.info(f"Chosen audio: {chosen_audio_path.name}")
            segment = normalize_dBFS(path=chosen_audio_path, target_dBFS=percentile_norms[j])
            segments_to_mix.append(segment)

        # mix chosen audio files
        # literally a canvas to put audio on
        canvas = AudioSegment.silent(duration=duration_ms)
        for j, path in enumerate(source_directories):
            segment = segments_to_mix[j]
            sc = random_coefficient()
            segment = segment - calculate_db_loss(sc)
            logger.info(f"Segment {j+1} coefficient: {sc} Volume: {segment.dBFS} dBFS")

            mixed_segment = mix_overlay(canvas, segment)

            chosen_volume = choose_volume(coefs=[canvas.dBFS, segment.dBFS], distr=distribution)
            mixed_segment = mixed_segment.apply_gain(volume_change=(chosen_volume - mixed_segment.dBFS))
            
            canvas = mixed_segment
            
        logger.info(f"Final volume: {canvas.dBFS} dBFS")
        mixed_segment.export(destination_directory / f"audio{i+1}.wav", format='wav')