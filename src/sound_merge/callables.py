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
    def __init__(self, audio_files: list[Path], duration_ms: int, percentile_norms: list[float], mix_func: callable, processing_funcs: list[callable]):
        self.audio_files = audio_files
        self.duration_ms = duration_ms
        self.percentile_norms = percentile_norms
        self.processing_funcs = processing_funcs
        self.mix_func = mix_func
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        processed_segments = []
        for audio_file in self.audio_files:
            segment = AudioSegment.from_file(audio_file)
            for func in self.processing_funcs:
                segment = func(segment) 
            processed_segments.append(segment)
        
        mixed_segment = self.mix_func(processed_segments)
        return mixed_segment

    
    
    