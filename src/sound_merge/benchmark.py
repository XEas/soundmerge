import random
import numpy as np
import logging
from typing import Union
from pathlib import Path
from pydub import AudioSegment
from augm import mix_overlay, random_segment, concatenate
from uniform import get_percentile_dBFS, normalize_dBFS

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
    Calculates the dB loss from the given percentage
    """
    return -10 * np.log10(percent)


def dynamic_select_benchmark(audio_file_count : int, destination_directory: Path, source_directories: list[Path], percentiles: list[float], distribution : str, duration: float, progress_bar=None):
    """
    Creates a testing benchmark with the given number of audio files, multiple directories, percentiles, distribution type
    """
    dir_norms = [get_percentile_dBFS(dir, percentile) for dir, percentile in zip(source_directories, percentiles)]
    for i in range(len(dir_norms)):
        logging.info(f"Dir {i+1} norm: {dir_norms[i]} dBFS")

    duration_ms = duration * 1000
    for i in range(audio_file_count):
        # literally a canvas to put audio on
        canvas = AudioSegment.silent(duration=duration_ms)
        logging.info(f"---------New Audio {i+1}---------")

        for j, path in enumerate(source_directories):
            audio = choose_audio(path=path)
            logging.info(f"Chosen audio: {audio.name}")
            segment = normalize_dBFS(audio, dir_norms[j])

            if len(segment) > duration_ms:
                segment = random_segment(segment, duration_ms)
            
            while len(segment) < duration_ms:
                extra_audio = choose_audio(path)
                extra_segment = normalize_dBFS(extra_audio, dir_norms[j])
                segment = concatenate(segment, extra_segment, crossfade_duration=100)

            sc = random_coefficient()
            segment = segment - calculate_db_loss(sc)
            logging.info(f"Segment {j+1} coefficient: {sc} Volume: {segment.dBFS} dBFS")

            mixed_segment = mix_overlay(canvas, segment)

            chosen_volume = choose_volume([canvas.dBFS, segment.dBFS], distribution)
            mixed_segment = mixed_segment.apply_gain(chosen_volume - mixed_segment.dBFS)
            
            canvas = mixed_segment
            
        
        logging.info(f"Final volume: {canvas.dBFS} dBFS")
        mixed_segment.export(destination_directory / f"audio{i+1}.wav", format='wav')
        
        # # progress bar used in GUI
        # if progress_bar:
        #     progress = ((i + 1) / num) * 100
        #     progress_bar['value'] = progress 
        #     root.update_idletasks()
