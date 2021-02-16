import pickle
import bz2

# Using bz2 wrapper to deal with pickle file size with large data


def load_pickle(filepath):
    with open(filepath, "rb") as f:
        return pickle.load(f)


def save_pickle(data, filepath):
    with open(filepath, "wb") as f:
        pickle.dump(data, f)


def load_bz2_pickle(filepath):
    with bz2.BZ2File(filepath, "rb") as f:
        return pickle.load(f)


def save_bz2_pickle(data, filepath):
    with bz2.BZ2File(filepath, "wb") as f:
        pickle.dump(data, f)
