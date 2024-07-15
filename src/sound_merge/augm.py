from pydub import AudioSegment
from pydub.playback import play
from config import *
from merge import WaveObject

music1 = AudioSegment.from_file(str(test_data / "music1.wav"), format="wav") # 44.1 kHz 16 bit
music2 = AudioSegment.from_file(str(test_data / "music2.wav"), format="wav") # 44.1 kHz 16 bit
speech1 = AudioSegment.from_file(str(test_data / "voice1.wav"), format="wav") # 44.1 kHz 16 bit
speech2 = AudioSegment.from_file(str(test_data / "voice2.wav"), format="wav") # 44.1 kHz 16 bit

