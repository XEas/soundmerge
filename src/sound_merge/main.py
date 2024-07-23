from benchmark_gui import simple_layout, dynamic_select_layout
from benchmark import simple_benchmark

def main(benchmark):
    dynamic_select_layout(benchmark)

if __name__ == "__main__":
    main(simple_benchmark)