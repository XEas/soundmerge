"""
This module contains callable classes that are used to generate audio segments
"""
from typing import Any
from pathlib import Path
from pydub import AudioSegment
from loguru import logger

class GenAudioFile:
    """
    Callable class that generates one audio segment from given list of audio segments 
    and parameters to augment/filter these segments. It also accepts a list of functions
    to process the audio segments.
    """
    def __init__(self, audio_files: list[Path], mix_func: callable, norm_func: callable, augm_funcs: list[callable], final_dBFS: float):
        self.audio_files = audio_files
        self.augm_funcs = augm_funcs
        self.norm_func = norm_func
        self.mix_func = mix_func
        self.final_dBFS = final_dBFS
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        processed_segments = []
        for audio_file in self.audio_files:
            segment = AudioSegment.from_file(audio_file)
            for func in self.augm_funcs:
                segment = func(segment, *kwds)
            processed_segments.append(segment)
        
        mixed_segment = processed_segments[0]
        for segment in processed_segments:
            mixed_segment = self.mix_func(segment, mixed_segment)
            mixed_segment = self.norm_func(mixed_segment, self.final_dBFS)
        return mixed_segment

    
    
    