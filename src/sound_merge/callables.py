"""
This module contains callable classes that are used to generate audio segments
"""
from pathlib import Path
from typing import Any, Callable

from loguru import logger
from pydub import AudioSegment


class GenAudioFile:
    """
    Callable class that generates one audio segment from given list of audio segments 
    and parameters to augment/filter these segments. It also accepts a list of functions
    to normalize, augment, and mix the audio segments.

    Parameters for __call__:
    - target_dBFS (float): The target dBFS for normalization.
    - length_ms (int)
    """
    def __init__(self, audio_files: list[Path], mix_func: Callable, norm_func: Callable, augm_funcs: list[Callable], final_dBFS: float):
        self.audio_files = audio_files
        self.augm_funcs = augm_funcs
        self.norm_func = norm_func
        self.mix_func = mix_func
        self.final_dBFS = final_dBFS
    def __call__(self, **kwargs: Any) -> Any:
        processed_segments = []
        for audio_file in self.audio_files:
            segment = AudioSegment.from_file(audio_file)
            for func in self.augm_funcs:
                segment = func(segment, **kwargs)
            processed_segments.append(segment)
        
        mixed_segment = processed_segments[0]
        for segment in processed_segments:
            mixed_segment = self.mix_func(sc1=1, sc2=0.5, audio_segment1=mixed_segment, audio_segment2=segment)
            mixed_segment = self.norm_func(segment=mixed_segment, target_dBFS=self.final_dBFS)
        return mixed_segment
