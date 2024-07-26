import random
from augm import *
import numpy as np
from uniform import *
import logging
from benchmark_gui import root
from typing import Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

pathlike = Union[str, Path]

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

def mixture(sc1 : float, sc2 : float, audio_segment1 : AudioSegment, audio_segment2 : AudioSegment) -> AudioSegment:
    """
    Mixes two audio segments with given coefficients
    """
    enh1 = audio_segment1 - calculate_db_loss(sc1)
    enh2 = audio_segment2 - calculate_db_loss(sc2)
    mixed_segment = mix_overlay(enh1, enh2)

    return mixed_segment

def choose_audio(path : Path) -> Path:
    """
    Chooses a random audio file from the given directory
    """
    audio_files = [file for file in path.glob('*.wav') if not file.name.startswith('._')] #ignore hidden files
    if audio_files:
        return random.choice(audio_files)
    return None

def calculate_db_loss(percent : float):
    """
    Calculates the dB loss from the given percentage
    """
    return -10 * np.log10(percent)


def dynamic_select_benchmark(num : int, dest: Path, dirs: list[Path], percentiles: list[float], distribution : str, duration: float, progress_bar=None):
    """
    Creates a testing benchmark with the given number of audio files, multiple directories, percentiles, distribution type
    """
    dir_norms = [get_percentile_dBFS(dir, percentile) for dir, percentile in zip(dirs, percentiles)]
    for i in range(len(dir_norms)):
        logging.info(f"Dir {i+1} norm: {dir_norms[i]} dBFS")

    for i in range(num):
        # literally a canvas to put audio on
        canvas = AudioSegment.silent(duration=duration)
        logging.info(f"---------New Audio {i+1}---------")

        for j, path in enumerate(dirs):
            audio = choose_audio(path=path)
            logging.info(f"Chosen audio: {audio.name}")
            segment = normalize_dBFS(audio, dir_norms[j])

            if len(segment) > duration:
                segment = random_segment(segment, duration)
            
            while len(segment) < duration:
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
        mixed_segment.export(dest / f"audio{i+1}.wav", format='wav')
        
        # # progress bar used in GUI
        # if progress_bar:
        #     progress = ((i + 1) / num) * 100
        #     progress_bar['value'] = progress 
        #     root.update_idletasks()
