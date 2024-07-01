#to do: fix the paths

import sys
sys.path.insert(1, "/Users/glebmokeev/Rask/sound-merge/src/sound_merge")

from merge import WaveObject

import wave
import numpy as np
import matplotlib.pyplot as plt

light_path = '/Users/glebmokeev/Rask/data/music-mixed/music-fma-wa-0055.wav' #16 kHz
light_path2 = '/Users/glebmokeev/Rask/data/music-clean/musdb-sample59.wav' #44.1 kHz

heavy_path = "/Users/glebmokeev/Rask/data/music-mixed/music-fma-wa-0013.wav" #16 kHz
heavy_path2 = "/Users/glebmokeev/Rask/data/music-clean/musdb-sample92.wav" #44.1 kHz

new_file_path = "/Users/glebmokeev/Rask/test_dest/new.wav"

def test_init():
    wf = WaveObject.from_wave_file(light_path)
    print(len(wf.audio_data))
    audio_array1 = np.frombuffer(wf.audio_data, dtype=np.int16).astype(np.float32) / 32768
    for i in range(1000):
        print(audio_array1[i])
    print(str(wf))
    
def test_display_waveform():
    wf = WaveObject.from_wave_file(heavy_path)
    wf.display_waveform()

def test_resample():
    resample_path = "/Users/glebmokeev/Rask/test_dest/resample.wav"
    wf = WaveObject.from_wave_file(light_path)
    wf_resampled = wf.resample_o(15000)
    wf_resampled.save_to_file(resample_path)

def test_concatenate():
    concatenate_path = "/Users/glebmokeev/Rask/test_dest/concatenate.wav"
    wf1 = WaveObject.from_wave_file(light_path)
    wf2 = WaveObject.from_wave_file(heavy_path)
    # wf_long = wf1.concatenate(heavy_path)
    wf_long = WaveObject.concatenate(wf1, wf2)

    wf_long.save_to_file(concatenate_path)

def test_mix():
    mix_path = "/Users/glebmokeev/Rask/test_dest/mix.wav"
    wf1 = WaveObject.from_wave_file(light_path2)
    wf2 = WaveObject.from_wave_file(heavy_path2)
    wf_mixed = WaveObject.mix(wf1, wf2, 0.1, 1.5)
    wf_mixed.save_to_file(mix_path)

def test():
    a = np.arange(6)
    print(a.reshape(-1, 2))

def test_play():
    wf1 = WaveObject.from_wave_file(light_path2)
    wf1.play()

def test_play_from_path():
    WaveObject.play_from_path(light_path2)

def test_time_segment():
    wf1 = WaveObject.from_wave_file(light_path)
    wf1.time_segment(5, 10).play()

def test_frame_segment():
    wf1 = WaveObject.from_wave_file(light_path)
    wf1.frame_segment(0, 80000).play()  

def test_display_spectogram():
    wf1 = WaveObject.from_wave_file(light_path)
    wf1.display_spectogram()

# test_concatenate()

# test_init()

# test_display_waveform()

# test_resample()

# test()

# test_mix()

# test_play()

# test_time_segment()

# test_frame_segment()

test_display_spectogram()