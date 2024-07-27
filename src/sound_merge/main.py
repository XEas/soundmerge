from benchmark_gui import dynamic_select_layout
from benchmark import bench
from pathlib import Path
import config

def main(benchmark):
    dynamic_select_layout(benchmark)

def run():
    src = config.music_detection
    dirs = [src / "test" / "music1", src / "test" / "speech1", src / "test" / "music2"]
    destination = src / "b1"
    bench(source_directories=dirs, destination_directory=destination, audio_file_count=3)
if __name__ == "__main__":
    run()