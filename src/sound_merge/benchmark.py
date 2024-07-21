import random
from augm import *
import numpy as np
from uniform import *
import logging

from benchmark_gui import root

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    return None

def calculate_db_loss(percent):
    return -10 * np.log10(percent)


def simple_benchmark(num, path, dir1, dir2, p1, p2, progress_bar):
    dir1_norm = get_percentile_dBFS(dir1, 0.95)
    logging.info(f"Dir 2 {p1 * 100} percentile: {dir1_norm} dBFS)")

    dir2_norm = get_percentile_dBFS(dir2, 0.95)
    logging.info(f"Dir 2 {p2 * 100} percentile: {dir2_norm} dBFS)")

    for i in range(num):
        audio_1 = choose_audio(dir1)
        segment_1 = normalize_dBFS(audio_1, dir1_norm)

        if len(segment_1) > 15000:
            segment_1 = random_segment(segment_1, 15000)
        
        while len(segment_1) < 15000:
            extra_audio = choose_audio(dir1)
            extra_segment = normalize_dBFS(extra_audio, dir1_norm)
            segment_1 = concatenate(segment_1, extra_segment, crossfade_duration=300)
        

        audio_2 = choose_audio(dir2)
        segment_2 = normalize_dBFS(audio_2, dir2_norm)

        if len(segment_2) > 10000:
            segment_2 = random_silence_mask(segment_2, total_silence_duration=3000, fade_duration=300)

        k1 = random_coefficient()
        k2 = random_coefficient()

        logging.info(f"Audio 1 coefficient: {k1} Audio 2 coefficient: {k2}")

        mixed_segment = mixture(k1, k2, segment_1, segment_2)
        chosen_volume = random.choice([segment_1.dBFS, segment_2.dBFS])
        mixed_segment = mixed_segment.apply_gain(chosen_volume - mixed_segment.dBFS)
        mixed_segment.export(path / f"audio{i+1}.wav", format='wav')

        progress = ((i + 1) / num) * 100
        progress_bar['value'] = progress 
        root.update_idletasks()