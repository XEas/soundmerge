import cProfile
import pstats
import wave
import numpy as np
from scipy.signal import resample

from merge import WaveObject

def test_resample():
    light_path = '/Users/glebmokeev/Rask/data/music-mixed/music-rfm-0128.wav'
    heavy_path = "/Users/glebmokeev/Rask/data/music-mixed/music-fma-0014.wav"
    heavy_path2 = "/Users/glebmokeev/Rask/data/music-clean/musdb-sample92.wav"
    wave_obj = WaveObject.from_wave_file(light_path)
    
    wave_obj.resample_pol(4000)

    wave_obj.save_to_file("/Users/glebmokeev/Rask/test_dest/fdsaf.wav")

def test_init():
    wf = WaveObject.from_wave_file("/Users/glebmokeev/Rask/data/music-mixed/music-rfm-0128.wav")
    print(wf.bytes_per_sample)

# cProfile.run('test_resample()', 'stats')
cProfile.run('test_init()', 'stats')

p = pstats.Stats('stats')

p.sort_stats('cumulative').print_stats()
