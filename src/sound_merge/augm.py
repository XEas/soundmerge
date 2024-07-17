from pydub import AudioSegment, effects
import random
import numpy as np
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

def mix_overlay(audio_segment1, audio_segment2, position=0, loop=False):
    return audio_segment1.overlay(audio_segment2, position=position, loop=loop)

def mix(audio_segment1, audio_segment2):
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

    mixed_audio_segment = AudioSegment(
        data=mixed_samples.astype(np.int16).tobytes(),
        sample_width=audio_segment1.sample_width,
        frame_rate=audio_segment1.frame_rate,
        channels=audio_segment1.channels
    )

    return mixed_audio_segment

def random_segment(audio_segment, length):
    start = random.randint(0, len(audio_segment) - length)
    return audio_segment[start:start + length]


def mix_alt(audiosegment1, audiosegment2):
    samples1 = np.array(audiosegment1.get_array_of_samples())
    samples2 = np.array(audiosegment2.get_array_of_samples())
    
    if len(samples1) < len(samples2):
        samples2 = samples2[:len(samples1)]

    mixed_array = np.zeros(len(samples1))

    for i in range(len(samples1)):
        if abs(samples1[i]) > abs(samples2[i]):
            mixed_array[i] = samples1[i]
        else:
            mixed_array[i] = samples2[i]

    mixed_audiosegment = AudioSegment(
        data=mixed_array.astype(np.int16).tobytes(),
        sample_width=audiosegment1.sample_width,
        frame_rate=audiosegment1.frame_rate,
        channels=audiosegment1.channels
    )

    return mixed_audiosegment