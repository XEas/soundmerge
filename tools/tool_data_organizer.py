import os
import shutil
import tarfile
import zipfile
from pathlib import Path

from tool_config import logger, data_dir, music_dir_clean, music_dir_mixed, speech_dir, libri_testset_dir, musan_speech_src, musan_music_src


# unpack .tar.gz archive
def unpack_tar(archive_path, dest_path):
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(dest_path)
    except tarfile.ReadError as e:
        logger.error(f"Error reading archive: {e}")
    except OSError as e:
        logger.error(f"Error during extraction: {e}")

# unpack zip archive
def unpack_zip(archive_path, dest_path):
    try:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_path)
    except zipfile.error as e:
        logger.error(f"Error reading archive: {e}")
    except OSError as e:
        logger.error(f"Error during extraction: {e}")
        
# copy dir of wav files
def copy_dir(src_dir : Path, dest_dir : Path, suffix : str):
    for item in src_dir.iterdir():
        src_path = src_dir / item.name
        dest_path = dest_dir / item.name
        if item.is_file() and item.suffix == f".{suffix}":
            try:
                shutil.copy(src_path, dest_path)
            except shutil.Error as e:
                logger.error(f"Error copying file: {e}")
        elif item.is_dir():
            copy_dir(src_path, dest_dir, suffix)

# copy file
def copy_file(src_path : Path, dest_dir : Path, suffix):
    if src_path.is_file() and src_path.suffix == f".{suffix}":
        try:
            dest_file = dest_dir / src_path.name
            shutil.copy(src_path, dest_file)
        except shutil.Error as e:
            logger.error(f"Error copying file: {e}")


# create necessary directories
os.makedirs(data_dir, exist_ok=True)
os.makedirs(music_dir_clean, exist_ok=True)
os.makedirs(music_dir_mixed, exist_ok=True)
os.makedirs(speech_dir, exist_ok=True)

copy_dir(libri_testset_dir, speech_dir, "wav")
copy_dir(musan_speech_src, speech_dir, "wav")
copy_dir(musan_music_src, music_dir_mixed, "wav")