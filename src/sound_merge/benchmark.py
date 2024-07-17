import random
from augm import *
from pathlib import Path
import numpy as np
from uniform import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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


def simple_benchmark(num, path, speech_dir, music_dir):
    speech_median = get_median_dBFS(speech_dir)
    logging.info(f"Dir 1 median: {speech_median} dBFS\n")
    music_median = get_median_dBFS(music_dir)
    logging.info(f"Dir 2 median: {music_median} dBFS\n")
    for i in range(num):
        audio_1 = choose_audio(speech_dir)
        segment_1 = normalize_dBFS(audio_1, speech_median)

        if len(segment_1) > 15000:
            segment_1 = random_segment(segment_1, 15000)
        
        while len(segment_1) < 15000:
            extra_audio = choose_audio(speech_dir)
            extra_segment = normalize_dBFS(extra_audio, speech_median)
            segment_1 = concatenate(segment_1, extra_segment, crossfade_duration=300)
        

        audio_2 = choose_audio(music_dir)
        segment_2 = normalize_dBFS(audio_2, music_median)

        if len(segment_2) > 10000:
            segment_2 = random_silence_mask(segment_2, total_silence_duration=3000, fade_duration=300)

        k1 = random_coefficient()
        k2 = random_coefficient()
        logging.info(f"Audio 1 coefficient: {k1} Audio 2 coefficient: {k2}\n")
        mixed_segment = mixture(k1, k2, segment_1, segment_2)
        chosen_volume = random.choice([segment_1.dBFS, segment_2.dBFS])
        mixed_segment = mixed_segment.apply_gain(chosen_volume - mixed_segment.dBFS)
        mixed_segment.export(path / f"audio{i+1}.wav", format='wav')
                           

    
if __name__ == '__main__':
    speech_dir = Path(input("Specify path to first directory you want to take audio from: "))
    music_dir = Path(input("Specify path to second directory you want to take audio from: "))
    num = int(input("Specify number of files you want to synthesize: "))
    if num > 500:
        logging.warning("Too many; number of files was set to 500")
        num = 500
    
    path = Path(input("Specify path to save files: "))

    simple_benchmark(num, path, speech_dir, music_dir)
    