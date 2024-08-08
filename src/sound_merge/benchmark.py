"""
This module contains the benchmark function that generates
audio files from the given source directories
"""

import random
from pathlib import Path
from typing import Iterable, Union, Callable, Generator

import numpy as np
from loguru import logger
from mutagen.wave import WAVE
from pydub import AudioSegment

from .augm import mix_overlay, random_segment
from .uniform import normalize_segment_dBFS
from .callables import GenAudioFile

PathLike = Union[str, Path]


def random_coefficient() -> float:
    """
    Generates a random coefficient between 0 and 1
    """
    return random.random()


def choose_volume(coefs: list, distr: str) -> float:
    """
    Chooses volume so the distribution of the coefficients is uniform or normal, as specified
    """
    coefs = [value for value in coefs if value > -np.inf]
    if distr == "uniform":
        return random.choice(coefs)
    if distr == "normal":
        return np.average(np.array(coefs))

    raise ValueError("Distribution type must be 'uniform' or 'normal'")


def calculate_db_loss(percent: float) -> float:
    """
    Calculates the dB loss from the given percentage.
    """
    if not 0 <= percent <= 1:
        raise ValueError("Percent must be between 0 and 1.")
    if percent == 0:
        raise ValueError(
            "Percent of 0 indicates infinite dB loss, which is not representable."
        )
    if percent == 1:
        return 0
    return -10 * np.log10(percent)


def take_clean_audio(audio_directory: Path) -> list[Path]:
    """
    Cleans the audio files from hidden files(MacOS)
    """
    clean_files = []
    for file in audio_directory.glob("*.wav"):
        if not file.name.startswith("."):
            clean_files.append(file)

    return clean_files


def filter_out_short_audio(audio_files: list[Path], duration_s: float) -> list[Path]:
    """
    Filters out audio files that are shorter than the given duration using mutagen
    """
    filtered = [
        audio
        for audio in audio_files
        if audio and WAVE(audio).info.length >= duration_s
    ]
    if len(filtered) == 0:
        raise ValueError("No audio files are long enough")
    return filtered


def mixture(
    sc1: float, sc2: float, audio_segment1: AudioSegment, audio_segment2: AudioSegment
) -> AudioSegment:
    """
    Mixes two audio segments with given coefficients
    """
    enh1 = audio_segment1 - calculate_db_loss(sc1)
    enh2 = audio_segment2 - calculate_db_loss(sc2)
    mixed_segment = mix_overlay(enh1, enh2)

    return mixed_segment


@logger.catch
def generate_source_audio(source_directories: Iterable[Path]) -> list[Path]:
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


def path_generator(
    source_directories: Iterable[Path],
    check_file: Callable[[Path], bool],
    n_generations: int,
) -> Generator[list[Path], None, None]:
    path_pool = []
    for directory in source_directories:
        paths = [
            path
            for path in directory.rglob("*")
            if path.is_file() and not path.name.startswith(".") and check_file(path)
        ]
        if len(paths) == 0:
            raise FileNotFoundError(f"No audio files found in: {directory}")
        path_pool.append(paths)

    for _ in range(n_generations):
        yield [random.choice(paths) for paths in path_pool]


def produce_benchmark(
    source_directories: list[Path], destination_directory: Path, audio_file_count: int
):
    """
    Benchmark function to test the dynamic selection of audio files
    """
    # source_files = generate_source_audio(source_directories=source_directories)

    gen_audio = GenAudioFile(
        mix_func=mixture,
        norm_func=normalize_segment_dBFS,
        augm_funcs=[random_segment, normalize_segment_dBFS],
        final_dbfs=-14,
        # target_dBFS=-14, length_s=1
    )

    paths = path_generator(
        source_directories=source_directories,
        check_file=gen_audio.check_file,
        n_generations=audio_file_count,
    )
    for i, audio_files in enumerate(paths):
        mixed_segment = gen_audio(audio_files=audio_files)
        dest_file = destination_directory / f"audio{i}.wav"
        mixed_segment.export(dest_file, format="wav")
        logger.info(f"Generated mixed file No.{i+1} saved to: {dest_file}")
