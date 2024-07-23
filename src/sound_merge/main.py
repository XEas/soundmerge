from benchmark_gui import simple_layout, dynamic_select_layout
from benchmark import simple_benchmark

def main(benchmark):
    dynamic_select_layout(benchmark)

def run():
    simple_benchmark(10, '/Users/glebmokeev/audio-projects/data/bchm', '/Users/glebmokeev/audio-projects/data/speech', '/Users/glebmokeev/audio-projects/data/music-clean', 0.95, 0.95, 'normal')

if __name__ == "__main__":
    run()