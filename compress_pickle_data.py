from pickle_util import load_pickle, save_bz2_pickle
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR / "data"

for file in DATA_DIR.glob('*.pickle'):
    data = load_pickle(file)
    save_bz2_pickle(data, file.with_suffix(".pbz2"))
