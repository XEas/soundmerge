import cProfile
import pstats
from config import * 

from merge import WaveObject

def test_resample():
    light_path = music_dir_mixed / "music-rfm-0128.wav"
    heavy_path = music_dir_mixed / "music-fma-0014.wav"
    heavy_path2 = music_dir_clean / "musdb-sample92.wav"
    wave_obj = WaveObject.from_wave_file(light_path)
    
    wave_obj.resample_o(4000)

    wave_obj.save_to_file(str(test_dest / "resample.wav"))


cProfile.run('test_resample()', 'stats')

p = pstats.Stats('stats')

p.sort_stats('cumulative').print_stats()
