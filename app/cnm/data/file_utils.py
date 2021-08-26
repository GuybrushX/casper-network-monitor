from pathlib import Path


def assure_dir_exists(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
