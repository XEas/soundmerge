from benchmark_gui import dynamic_select_layout
from benchmark import dynamic_select_benchmark
from pathlib import Path
import config

def main(benchmark):
    dynamic_select_layout(benchmark)

def run():
    src = config.music_detection
    dirs = [src / "test" / "music1", src / "test" / "speech1", src / "test" / "music2"]
    destination = src / "b1"
    dynamic_select_benchmark(audio_file_count=10, destination_directory=destination, source_directories=dirs, percentiles=[0.95, 0.95, 0.95], distribution='normal', duration=30)

if __name__ == "__main__":
    run()