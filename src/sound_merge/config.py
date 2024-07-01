from pathlib import Path
import logging
home = Path("/Users/glebmokeev/Rask")
data_dir = home / "data"
music_dir_clean = data_dir / "music-clean"
music_dir_mixed = data_dir / "music-mixed"
speech_dir = data_dir / "speech"

test_dest = data_dir / "test_dest"

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)