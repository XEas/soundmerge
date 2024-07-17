import random
from augm import *
from config import *
import numpy as np
from uniform import *

"""Two directories of normalized sound files.
    1. Randomly choose speech
    2. Randomly choose background
    3. Randomly choose two coefficients 0-1 for loudness                

"""

def random_coefficient():
    return random.random()

def new_volume(sc1, sc2):
    random.choice([sc1, sc2])

def mixture(sc1, sc2, audio_segment1, audio_segment2):
    enh1 = audio_segment1 - calculate_db_loss(sc1)
    enh2 = audio_segment2 - calculate_db_loss(sc2)
    logger.info(f"Audio 1 coefficient: {sc1} Audio 2 coefficient: {sc2}")
    mixed_segment = mix_overlay(enh1, enh2)

    return mixed_segment

def choose_audio(path):
    audio_files = [file for file in path.glob('*.wav') if not file.name.startswith('._')]
    if audio_files:
        return random.choice(audio_files)
    else:
        return None

def calculate_db_loss(percent):
    return -10 * np.log10(percent)

def new_audio():
    audio_1 = choose_audio(speech_dir)
    segment_1 = AudioSegment.from_file(audio_1)

    audio_2 = choose_audio(music_dir_clean)
    segment_2 = AudioSegment.from_file(audio_2)

    k1 = random_coefficient()
    k2 = random_coefficient()

    mixed_segment = mixture(k1, k2, segment_1, segment_2)

    return mixed_segment

def simple_benchmark(num, path, speech_dir, music_dir):
    speech_median = get_median_dBFS(speech_dir)
    music_median = get_median_dBFS(music_dir)
    
    for i in range(num):
        
        audio_1 = choose_audio(speech_dir)
        # audio_1 = normalize_dBFS(audio_1, speech_median)
        segment_1 = AudioSegment.from_file(audio_1)

        audio_2 = choose_audio(music_dir)
        # audio_2 = normalize_dBFS(audio_2, music_median)
        segment_2 = AudioSegment.from_file(audio_2)

        k1 = random_coefficient()
        k2 = random_coefficient()

        mixed_segment = mixture(k1, k2, segment_1, segment_2)
        mixed_segment.export(path / f"audio{i+1}.wav", format='wav')
                           

    
if __name__ == '__main__':
    speech_dir = Path(input("Specify path to first directory you want to take audio from: "))
    music_dir = Path(input("Specify path to second directory you want to take audio from: "))
    num = int(input("Specify number of files you want to synthesize:"))
    if num > 500:
        print("Too many; number of files was set to 500")
        num = 500
    path = Path(input("Specify path to save files: "))
    speech_dir = Path("/Users/glebmokeev/audio-projects/data/speech")
    music_dir = Path("/Users/glebmokeev/audio-projects/data/music-clean")
    path = Path("/Users/glebmokeev/benchs")

    simple_benchmark(num, path, speech_dir, music_dir)
    