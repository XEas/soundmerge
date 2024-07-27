import random
import numpy as np
import logging
from typing import Union, Iterable, List
from pathlib import Path
from pydub import AudioSegment
from augm import mix_overlay, random_segment
from uniform import normalize_segment_dBFS
from mutagen.wave import WAVE
from callables import GenAudioFile
from loguru import logger

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PathLike = Union[str, Path]

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
    if distr == 'normal':
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
    if percent == 1:
        return 0
    return -10 * np.log10(percent)

def take_clean_audio(audio_directory : Path) -> list[Path]:
    """
    Cleans the audio files from hidden files
    """
    clean_files = [file for file in audio_directory.glob('*.wav') if not file.name.startswith('._')] # ignore hidden files

    return clean_files

def filter_out_short_audio(audio_files: list[Path], duration_s: float) -> list[Path]:
    """
    Filters out audio files that are shorter than the given duration using mutagen
    """
    filtered = [audio for audio in audio_files if audio and WAVE(audio).info.length >= duration_s]
    if len(filtered) == 0:
        raise ValueError("No audio files are long enough")
    return filtered

def mixture(sc1 : float, sc2 : float, audio_segment1 : AudioSegment, audio_segment2 : AudioSegment) -> AudioSegment:
    """
    Mixes two audio segments with given coefficients
    """
    enh1 = audio_segment1 - calculate_db_loss(sc1)
    enh2 = audio_segment2 - calculate_db_loss(sc2)
    mixed_segment = mix_overlay(enh1, enh2)

    return mixed_segment

@logger.catch
def generate_source_audio(source_directories : Iterable[Path]) -> list[Path]:
    """
    Generates source audio files from the given directories - one from each directory
    returns:
    list of paths to the chosen audio files
    """
    files = []
    for directory in source_directories:
        clean_files = take_clean_audio(audio_directory=directory)
        approp_files = filter_out_short_audio(audio_files=clean_files, duration_s=1)
        chosen_file = random.choice(approp_files)
        files.append(chosen_file)
        logger.info(f"Chosen audio file: {chosen_file}")
    return files

def bench(source_directories: list[Path], destination_directory: Path, audio_file_count: int):
    """
    Benchmark function to test the dynamic selection of audio files
    """
    source_files = generate_source_audio(source_directories=source_directories)
    gen_audio = GenAudioFile(
        audio_files=source_files,
        mix_func=mixture,
        norm_func=normalize_segment_dBFS,
        augm_funcs=[random_segment, normalize_segment_dBFS],
        final_dBFS=-14
    )

    for i in range(audio_file_count):
        mixed_segment = gen_audio(target_dBFS=-14, length_s=1)
        mixed_segment.export(destination_directory / f"audio{i}.wav", format="wav")
        logger.info(f"Generated mixed file No.{i+1} saved to: {destination_directory / f"audio{i}.wav"}")
