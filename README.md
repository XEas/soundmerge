# Soundmerge

Soundmerge is a powerful tool for creating audio benchmarks for background music detection models

## Features

- Supports WAV files
- Median normalization
- Silence masks
- Other customizable augmentations
- Volume/clipping control


## Installation

To install soundmerge, follow these steps:

1. Clone the repository: `git clone https://github.com/XEas/soundmerge.git`
2. Navigate to the project directory: `cd soundmerge`
3. Install poetry: `curl -sSL https://install.python-poetry.org | python3 -`
4. Intall dependencies: `poetry install`


## Quick Start

Create a benchmark: `poetry run python src/sound_merge/benchmark.py`


## License

Soundmerge is released under the [MIT License](https://opensource.org/licenses/MIT). Feel free to use, modify, and distribute this repo.
