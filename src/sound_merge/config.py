from pathlib import Path
import logging
home = Path("/Users/glebmokeev/audio-projects")
data_dir = home / "data"
music_dir_clean = data_dir / "music-clean"
music_dir_mixed = data_dir / "music-mixed"
speech_dir = data_dir / "speech"

test_dest = data_dir / "test_dest"

tests_path = home / "sound-merge/tests"
test_data = tests_path / "data"

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

light_path = music_dir_mixed / "music-fma-wa-0055.wav" #16 kHz
light_path2 = music_dir_clean / "musdb-sample59.wav" #44.1 kHz

heavy_path = music_dir_mixed / "music-fma-wa-0013.wav" #16 kHz
heavy_path2 = music_dir_clean / "musdb-sample92.wav" #44.1 kHz

new_file_path = test_dest / "new.wav"
