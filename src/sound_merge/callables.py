"""
This module contains callable classes that are used to generate audio segments
"""

from pathlib import Path
from typing import Any, Callable

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

    def __init__(
        self,
        mix_func: Callable,
        norm_func: Callable,
        augm_funcs: list[Callable],
        final_dbfs: float,
    ):
        # self.audio_files = audio_files
        self._augm_funcs = augm_funcs
        self._norm_func = norm_func
        self._mix_func = mix_func
        self._final_dbfs = final_dbfs

    def __call__(self, audio_files: list[Path], **kwargs: Any) -> AudioSegment:
        processed_segments = []
        for audio_file in audio_files:
            segment = AudioSegment.from_file(audio_file)
            for func in self._augm_funcs:
                segment = func(segment, **kwargs)
            processed_segments.append(segment)

        mixed_segment = processed_segments[0]
        for segment in processed_segments:
            mixed_segment = self._mix_func(
                sc1=1, sc2=0.5, audio_segment1=mixed_segment, audio_segment2=segment
            )
            mixed_segment = self._norm_func(
                segment=mixed_segment, target_dBFS=self._final_dbfs
            )
        return mixed_segment

    def check_file(self, audio_file: Path) -> bool:
        return True
