"""
This module contains callable classes that are used to generate audio segments
"""

from abc import ABC, abstractmethod
from pathlib import Path
import random

import numpy as np
from pydub import AudioSegment  # type: ignore


# class GenAudioFile:
#     """
#     Callable class that generates one audio segment from given list of audio segments
#     and parameters to augment/filter these segments. It also accepts a list of functions
#     to normalize, augment, and mix the audio segments.

#     Parameters for __call__:
#     - target_dBFS (float): The target dBFS for normalization.
#     - length_ms (int)
#     """

#     def __init__(
#         self,
#         mix_func: Callable,
#         norm_func: Callable,
#         augm_funcs: list[Callable],
#         final_dbfs: float,
#     ):
#         # self.audio_files = audio_files
#         self._augm_funcs = augm_funcs
#         self._norm_func = norm_func
#         self._mix_func = mix_func
#         self._final_dbfs = final_dbfs

#     def __call__(self, audio_files: list[Path], **kwargs: Any) -> AudioSegment:
#         processed_segments = []
#         for audio_file in audio_files:
#             segment = AudioSegment.from_file(audio_file)
#             for func in self._augm_funcs:
#                 segment = func(segment, **kwargs)
#             processed_segments.append(segment)

#         mixed_segment = processed_segments[0]
#         for segment in processed_segments:
#             mixed_segment = self._mix_func(
#                 sc1=1, sc2=0.5, audio_segment1=mixed_segment, audio_segment2=segment
#             )
#             mixed_segment = self._norm_func(
#                 segment=mixed_segment, target_dBFS=self._final_dbfs
#             )
#         return mixed_segment

#     def check_file(self, audio_file: Path) -> bool:
#         return True


class PipelineStep(ABC):
    """
    Base abstract class for a pipeline step.
    """


class FileBasedPipelineStep(PipelineStep):
    """
    Abstract class for pipeline steps that operate on file paths.
    """

    @abstractmethod
    def __call__(self, source_dirs: list[Path]) -> list[AudioSegment]:
        pass


class SegmentBasedPipelineStep(PipelineStep):
    """
    Abstract class for pipeline steps that operate on AudioSegment objects.
    """

    @abstractmethod
    def __call__(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        pass


class PullAudioSegments(FileBasedPipelineStep):
    """
    A pipeline step that pulls an audio file from each directory.

    Takes a list of directories and returns a list of audiosegments.
    """

    def __call__(self, source_dirs: list[Path]) -> list[AudioSegment]:
        chosen_files = []
        for directory in source_dirs:
            paths = [
                path
                for path in directory.rglob("*")
                if path.is_file()
                and not path.name.startswith(".")
                and self._check_file(path)
            ]
            if len(paths) == 0:
                raise FileNotFoundError(f"No audio files found in: {directory}")
            chosen_files.append(AudioSegment.from_file(random.choice(paths)))
        return chosen_files

    def _check_file(self, audio_file: Path) -> bool:
        return True


class RandomSegment(SegmentBasedPipelineStep):
    """
    A pipeline step that generates a random segment from an audio file.
    """

    def random_segment(self, audio_segment: AudioSegment) -> AudioSegment:
        length_ms = int(1000 * self._len_s)
        if len(audio_segment) <= length_ms:
            return audio_segment
        start = random.randint(0, len(audio_segment) - length_ms)
        return audio_segment[start : start + length_ms]

    def __init__(self, len_s: float):
        self._len_s = len_s

    def __call__(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        return [self.random_segment(audio_segment) for audio_segment in audio_segments]


class NormalizeSegments(SegmentBasedPipelineStep):
    """
    A pipeline step that normalizes an audio segment.
    """

    def __init__(self, target_dBFS: float):
        self._target_dBFS = target_dBFS

    def __call__(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        return [
            audio_segment.apply_gain(self._target_dBFS - audio_segment.dBFS)
            for audio_segment in audio_segments
        ]


class MixSegments(SegmentBasedPipelineStep):
    """
    A pipeline step that mixes audio segments.
    """

    def _calculate_db_loss(self, percent: float) -> float:
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

    def _mix_w_coef(
        self,
        sc1: float,
        sc2: float,
        audio_segment1: AudioSegment,
        audio_segment2: AudioSegment,
    ) -> AudioSegment:
        """
        Mixes two audio segments with given coefficients
        """
        enh1 = audio_segment1 - self._calculate_db_loss(sc1)
        enh2 = audio_segment2 - self._calculate_db_loss(sc2)
        mixed_segment = enh1.overlay(enh2)

        return mixed_segment

    def __call__(self, audio_segments: list[AudioSegment]) -> list[AudioSegment]:
        mixed_segment = audio_segments[0]
        for segment in audio_segments[1:]:
            mixed_segment = self._mix_w_coef(
                sc1=1, sc2=0.5, audio_segment1=mixed_segment, audio_segment2=segment
            )
        return mixed_segment
