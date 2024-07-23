from benchmark_gui import simple_layout, dynamic_select_layout
from benchmark import simple_benchmark, dynamic_select_benchmark
from pathlib import Path

def main(benchmark):
    dynamic_select_layout(benchmark)

def run():
    src = Path("/Volumes/Drive-1/music-detection/")
    dirs = [src / "test" / "music1", src / "test" / "speech1"]
    destination = src / "b1"
    # simple_benchmark(10, '/Users/glebmokeev/audio-projects/data/bchm', '/Users/glebmokeev/audio-projects/data/speech', '/Volumes/Drive-1/music-detection/test/music1', 0.95, 0.95, 'normal')
    dynamic_select_benchmark(10, destination, dirs, [0.95, 0.95], 'normal', 10000)

if __name__ == "__main__":
    run()