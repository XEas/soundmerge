"""Two directories of normalized sound files.
    1. Randomly choose speech
    2. Randomly choose background
    3. Randomly choose two coefficients 0-1 for loudness                

"""
import random
from augm import *
from config import *

def random_coefficient():
    return random.random()

def new_volume(k1, k2):
    random.choice([k1, k2])

def generate_mixture(k1, k2, audio_segment1, audio_segment2):
    enh1 = audio_segment1.apply_gain(k1)
    enh2 = audio_segment2.apply_gain(k2)

    mixed_segment = enh1.overlay(enh2, position=0, loop=False)

    return mixed_segment

def choose_audio(path):
    audio_files = list(path.glob('*.wav'))
    if audio_files:
        return random.choice(audio_files)
    else:
        return None


def generate_simple_benchmark():
    pass