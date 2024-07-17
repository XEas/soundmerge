import random
from augm import *
from config import *
import numpy as np

"""Two directories of normalized sound files.
    1. Randomly choose speech
    2. Randomly choose background
    3. Randomly choose two coefficients 0-1 for loudness                

"""

def random_coefficient():
    return random.random()

def new_volume(sc1, sc2):
    random.choice([sc1, sc2])

def mix(sc1, sc2, audio_segment1, audio_segment2):
    enh1 = audio_segment1 - calculate_db_loss(sc1)
    enh2 = audio_segment2 - calculate_db_loss(sc2)

    mixed_segment = enh1.overlay(enh2, position=0, loop=False)

    return mixed_segment

def choose_audio(path):
    audio_files = list(path.glob('*.wav'))
    if audio_files:
        return random.choice(audio_files)
    else:
        return None

def calculate_db_loss(percent):
    return -10 * np.log10(percent)

def new_audio():
    audio_1 = choose_audio(speech_dir)
    segment_1 = AudioSegment.from_file(audio_1)

    audio_2 = choose_audio(music_dir_mixed)
    segment_2 = AudioSegment.from_file(audio_2)

    k1 = random_coefficient()
    k2 = random_coefficient()

    mixed_segment = mix(k1, k2, segment_1, segment_2)

    return mixed_segment



for i in range(10):
    new_audio().export(str(benchmark_path / 'b1' / f'mxied{i}.wav'), format='wav')


    