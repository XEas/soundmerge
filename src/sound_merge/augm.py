from pydub import AudioSegment

from config import *
from merge import WaveObject

music1 = AudioSegment.from_file(str(test_data / "music1.wav"), format="wav")
music2 = AudioSegment.from_file(str(test_data / "music2.wav"), format="wav")
speech1 = AudioSegment.from_file(str(test_data / "voice1.wav"), format="wav")
speech2 = AudioSegment.from_file(str(test_data / "voice2.wav"), format="wav")

music_loudness1 = music1.dBFS
music_loudness2 = music2.dBFS

peak_amplitude = music2.max

print(peak_amplitude)