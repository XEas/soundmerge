from pathlib import Path
import logging

dataset_dir = Path("/Volumes/Drive-1/Datasets/speech_unpacked")
libri_testset_dir = dataset_dir / "LibriTTS_R"
musan_music_src = dataset_dir / "musan/music"
musan_speech_src = dataset_dir / "musan/speech"

#destination paths
data_dir = Path("/Users/glebmokeev/Rask/data")
music_dir_clean = data_dir / "music-clean"
music_dir_mixed = data_dir / "music-mixed"
speech_dir = data_dir / "speech"

#logger config
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)