import os
import shutil
from pathlib import Path
import logging

import stempeg #type: ignore
from pydub import AudioSegment #type: ignore
from tool_config import dataset_dir, logger


def extract_stems(stem_file, output_dir):
    data, sample_rate = stempeg.read_stems(stem_file)
    num_stems = len(data)

    for i in range(num_stems):
        stem_name = f"stem_{i+1}.wav"
        output_path = output_dir / stem_name
        stempeg.write_audio(str(output_path), data[i], sample_rate, codec="pcm_s16le")


def process_stems(stem_dir: Path, output_dir: Path):
    files_failed = 0
    i = 1
    for item in stem_dir.iterdir():
        if item.is_file():
            try:
                if item.suffix == ".mp4" and not (item.name.startswith("._")):
                    filename_new = f"musdb-sample{i}.wav"

                    output_dir = stem_dir / filename_new
                    os.makedirs(output_dir, exist_ok=True)
                    extract_stems(str(stem_dir / item.name), output_dir)

                    stem_2 = AudioSegment.from_wav(
                        os.path.join(output_dir, "stem_2.wav")
                    )
                    stem_3 = AudioSegment.from_wav(
                        os.path.join(output_dir, "stem_3.wav")
                    )
                    stem_4 = AudioSegment.from_wav(
                        os.path.join(output_dir, "stem_4.wav")
                    )
                    combined_sound = stem_2 + stem_3 + stem_4

                    output_file = output_dir / filename_new
                    combined_sound.export(output_file, format="wav")

                    i += 1
                    logging.info(f"Extracted file {i-1}: {item.name}")
            except shutil.Error as e:
                logger.error(f"Error {files_failed} extracting file: {e}")
                files_failed += 1
        elif item.is_dir():
            process_stems(stem_dir / item.name, i)


stem_dir = dataset_dir / "musdb18"

process_stems(stem_dir, output_dir=Path("/Volumes/Drive-1/musdb-converted"))
