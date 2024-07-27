import random

import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from scipy.signal import spectrogram


def random_silence_mask(audio_segment, total_silence_duration, silence_interval_duration, fade_duration):
    """
    Randomly masks audio_segment with silence intervals of specified lenght
    """
    total_silence_duration = min(total_silence_duration, len(audio_segment))
    num_intervals = total_silence_duration // silence_interval_duration

    start_points = sorted(random.sample(range(0, len(audio_segment) - silence_interval_duration), num_intervals))
    modified_audio = audio_segment[:]

    for start in start_points:
        end = start + silence_interval_duration
        start_audio = modified_audio[:start].fade_out(min(fade_duration, start))

        end_audio = modified_audio[end:].fade_in(min(fade_duration, len(modified_audio) - end))

        modified_audio = start_audio + AudioSegment.silent(duration=silence_interval_duration) + end_audio
        
    return modified_audio


def concatenate(audio_segment1: AudioSegment, audio_segment2: AudioSegment, crossfade_duration: int = 0) -> AudioSegment:
    return audio_segment1.append(audio_segment2, crossfade=crossfade_duration)

def mix_overlay(audio_segment1: AudioSegment, audio_segment2: AudioSegment, position: int = 0, loop: bool = False, **kwargs) -> AudioSegment:
    return audio_segment1.overlay(audio_segment2, position=position, loop=loop)


def mix(audio_segment1: AudioSegment, audio_segment2: AudioSegment) -> AudioSegment:
    """
    Mixes two audio segments by adding them and normalizing by dividing by the max value
    """
    samples1 = np.array(audio_segment1.get_array_of_samples(), dtype=np.float32) / audio_segment1.max_possible_amplitude
    samples2 = np.array(audio_segment2.get_array_of_samples(), dtype=np.float32) / audio_segment2.max_possible_amplitude

    if len(samples1) < len(samples2):
        samples2 = samples2[:len(samples1)]
    else:
        samples2 = np.pad(samples2, (0, len(samples1) - len(samples2)), 'constant')

    mixed_samples = samples1 + samples2

    peak = np.abs(mixed_samples).max()
    if peak > 1:
        mixed_samples /= peak

    mixed_samples *= audio_segment1.max_possible_amplitude

    # create a new audio segment from the mixed samples
    mixed_audio_segment = AudioSegment(
        data=mixed_samples.astype(np.int16).tobytes(),
        sample_width=audio_segment1.sample_width,
        frame_rate=audio_segment1.frame_rate,
        channels=audio_segment1.channels
    )

    return mixed_audio_segment

def random_segment(audio_segment: AudioSegment, length_s: float, **kwargs) -> AudioSegment:
    """
    Cuts out a random segment of the given length in miliseconds from the audio segment
    """
    length_ms = int(1000 * length_s)
    start = random.randint(0, len(audio_segment) - length_ms)
    return audio_segment[start:(start + length_ms)]

def display_spectrogram(audio_segment: AudioSegment):
        """
        Displays the spectrogram of the audio segment
        """
        samples = np.array(audio_segment.get_array_of_samples())
        
        num_channels = audio_segment.channels
        if num_channels == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)
        
        f, t, Sxx = spectrogram(samples, audio_segment.frame_rate)
        plt.figure(figsize=(10, 4))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Spectrogram')
        plt.colorbar(label='Intensity [dB]')
        plt.show()

def display_waveform(audio_segment: AudioSegment):
        """
        Displays the waveform of the audio segment
        """
        samples = np.array(audio_segment.get_array_of_samples())
        
        num_channels = audio_segment.channels
        if num_channels == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)
        
        plt.figure(figsize=(10, 4))
        plt.plot(samples)
        plt.title('Wave File Plot')
        plt.xlabel('Frame')
        plt.ylabel('Amplitude')
        plt.show()