import pickle
import bz2

# Using bz2 wrapper to deal with pickle file size with large data


def load_pickle(filepath):
    with open(filepath, "rb") as f:
        return pickle.load(f)


def save_pickle(data, filepath):
    with open(filepath, "wb") as f:
        try:
            pickle.dump(data, f)
        except TypeError as e:
            print(pickle_trick(data))
            raise e


def load_bz2_pickle(filepath):
    with bz2.BZ2File(filepath, "rb") as f:
        return pickle.load(f)


def save_bz2_pickle(data, filepath):
    with bz2.BZ2File(filepath, "wb") as f:
        pickle.dump(data, f)


def pickle_trick(obj, max_depth=10):
    output = {}

    if max_depth <= 0:
        return output

    try:
        pickle.dumps(obj)
    except (pickle.PicklingError, TypeError) as e:
        failing_children = []

        if hasattr(obj, "__dict__"):
            for k, v in obj.__dict__.items():
                result = pickle_trick(v, max_depth=max_depth - 1)
                if result:
                    failing_children.append(result)

        output = {
            "fail": obj,
            "err": e,
            "depth": max_depth,
            "failing_children": failing_children
        }

    return output
