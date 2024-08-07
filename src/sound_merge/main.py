import config
from benchmark import produce_benchmark


def run():
    src = config.music_detection
    dirs = [src / "test" / "music1", src / "test" / "speech1", src / "test" / "music2"]
    destination = src / "b1"

    produce_benchmark(
        source_directories=dirs, destination_directory=destination, audio_file_count=3
    )


if __name__ == "__main__":
    run()
