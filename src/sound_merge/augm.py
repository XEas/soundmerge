from pydub import AudioSegment, effects
import random

random.seed(42)

def random_silence_mask(audio_segment, total_silence_duration):
    total_silence_duration = min(total_silence_duration, len(audio_segment))

    silence_interval_duration = 1000 
    num_intervals = total_silence_duration // silence_interval_duration

    start_points = sorted(random.sample(range(0, len(audio_segment) - silence_interval_duration), num_intervals))
    modified_audio = audio_segment[:]

    for start in start_points:
        silence_segment = AudioSegment.silent(duration=silence_interval_duration)

        modified_audio = modified_audio[:start] + silence_segment + modified_audio[start + silence_interval_duration:]

    return modified_audio

def fade():
    pass



