from pydub import AudioSegment, effects
import random

random.seed(42)

def random_silence_mask(audio_segment, total_silence_duration, silence_interval_duration=1000, fade_duration=200):
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


def concatenate(audio_segment1, audio_segment2, crossfade_duration=0):
    return audio_segment1.append(audio_segment2, crossfade=crossfade_duration)

def mix(audio_segment1, audio_segment2):
    return audio_segment1.overlay(audio_segment2, position=0, gain_during_overlay=-6, loop=False)

def random_segment(audio_segment, length):
    start = random.randint(0, len(audio_segment) - length)
    return audio_segment[start:start + length]
