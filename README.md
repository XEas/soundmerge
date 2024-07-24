# Soundmerge

Soundmerge is a powerful tool for creating audio benchmarks for background music detection models

## Features

- Supports WAV files
- Percentile normalization
- Silence masks
- Other customizable augmentations
- Volume/clipping control
- Allows for multiple Directories
- GUI


## Installation

To install soundmerge, follow these steps:

1. Clone the repository: `git clone https://github.com/XEas/soundmerge.git`
2. Navigate to the project directory: `cd soundmerge`
3. Install poetry: `curl -sSL https://install.python-poetry.org | python3 -`
4. Intall dependencies: `poetry install`


## Quick Start

Create a benchmark: 
1. `poetry shell`
2. `poetry run python src/sound_merge/main.py `
To use with GUI, in `main.py` change `run()` to `main()`


## License

Soundmerge is released under the [MIT License](https://opensource.org/licenses/MIT). Feel free to use, modify, and distribute this repo.
