import os
import pandas as pd

import string
from abc import *
from typing import Set

import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
import jsonpickle.ext.pandas as jsonpickle_pandas
jsonpickle_numpy.register_handlers()
jsonpickle_pandas.register_handlers()

#
class SimpleDict(ABC):
    """Dict-like class that only accepts keys which are sequences of strings.

    An abstract class for a key-value store. It accepts keys in a form of
    either a single sting or a sequence (tuple, list, etc.) of strings.
    It imposes no restrictions on types of values in the key-value pairs.

    The API for the class resemples the API of Python's built-in Dict.
    """

    allowed_key_chars: Set = set(string.ascii_letters
                                 + string.digits + "()_-.=")

    def _normalize_key(self, key):
        """Check if a key meets requirements and return its standardized form.

        A key must be either a string or a sequence of non-empty strings.
        If it is a single string, it will be transformed into a tuple,
        consisting of this sole string.

        Each string in a sequence can contain only alphanumerical characters
        and characters from this list: ()_-.=
        """

        if isinstance(key, str):
            key = (key,)
        key = tuple(str(s) for s in key)
        for s in key:
            assert len(set(s) - self.allowed_key_chars) == 0
            assert len(s)
        return key

    @abstractmethod
    def __contains__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, key, vlaue):
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def _generic_iter(self, iter_type: str):
        assert iter_type in {"keys", "values", "items"}
        raise NotImplementedError

    def __iter__(self):
        return self._generic_iter("keys")

    def keys(self):
        return self._generic_iter("keys")

    def values(self):
        return self._generic_iter("values")

    def items(self):
        return self._generic_iter("items")

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def pop(self, key, default):
        if key in self:
            result = self[key]
            del self[key]
            return result
        else:
            return default

    def popitem(self):
        key = next(iter(self))
        result = self[key]
        del self[key]
        return result

    def __eq__(self, other):
        try:
            if len(self) != len(other):
                return False
            for k in self.keys():
                if self[k] != other[k]:
                    return False
            return True
        except:
            return False

    def __ne__(self, other):
        return not (self == other)

    def clear(self):
        for k in self.keys():
            del self[k]


class FileDirDict(SimpleDict):
    """ A persistent Dict that stores key-value pairs in local files.

    A new file is created for each key-value pair.
    A key is either a filename (without an extension),
    or a sequence of directory names that ends with a filename.
    A value can be any Python object, which is stored in a file.

    FileDirDict can store objects in binary files (as pickles)
    or in human-readable text files (using jsonpickles).
    """

    def __init__(self, dir_name: str = "FileDirDict", file_type: str = "pkl"):
        """A constructor defines location of the store and file format to use.

        dir_name is a directory that will contain all the files in
        the FileDirDict. If the directory does not exist, it will be created.

        file_type can take one of two values: "pkl" or "json".
        It defines which file format will be used by FileDirDict
        to store values.
        """

        self.file_type = file_type

        assert file_type in {"json", "pkl"}, (
            "file_type must be either pkl or json")
        assert not os.path.isfile(dir_name)
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        assert os.path.isdir(dir_name)

        self.base_dir = os.path.abspath(dir_name)

    def __len__(self):
        num_files = 0
        for subdir_info in os.walk(self.base_dir):
            files = subdir_info[2]
            files = [f_name for f_name in files
                     if f_name.endswith(self.file_type)]
            num_files += len(files)
        return num_files

    def clear(self):
        for subdir_info in os.walk(self.base_dir, topdown=False):
            (subdir_name, _, files) = subdir_info
            num_files = len(files)
            for f in files:
                if f.endswith(self.file_type):
                    os.remove(os.path.join(subdir_name, f))
            if (subdir_name != self.base_dir) and len(os.listdir(subdir_name)) == 0:
                os.rmdir(subdir_name)

    def _build_full_filename(self, key, create_subdirs=False):
        key = self._normalize_key(key)
        key = [self.base_dir] + list(key)
        dir_names = key[:-1]

        if create_subdirs:
            current_dir = key[0]
            for dir_name in key[1:-1]:
                new_dir = os.path.join(current_dir, dir_name)
                if not os.path.isdir(new_dir):
                    os.mkdir(new_dir)
                current_dir = new_dir

        file_name = key[-1] + "." + self.file_type
        return os.path.join(*dir_names, file_name)

    def _read_from_file(self, file_name: str):
        if self.file_type == "pkl":
            result = pd.read_pickle(file_name)
        elif self.file_type == "json":
            with open(file_name, 'r') as f:
                result = jsonpickle.loads(f.read())
        else:
            raise ValueError("file_type must be either pkl or json")
        return result

    def _save_to_file(self, file_name: str, value):
        if self.file_type == "pkl":
            pd.to_pickle(value, file_name)
        elif self.file_type == "json":
            with open(file_name, 'w') as f:
                f.write(jsonpickle.dumps(value, indent=4))
        else:
            raise ValueError("file_type must be either pkl or json")

    def __contains__(self, key):
        filename = self._build_full_filename(key)
        return os.path.isfile(filename)

    def __getitem__(self, key):
        filename = self._build_full_filename(key)
        if not os.path.isfile(filename):
            raise KeyError(f"File {filename} does not exist")
        result = self._read_from_file(filename)
        return result

    def __setitem__(self, key, value):
        filename = self._build_full_filename(key, create_subdirs=True)
        self._save_to_file(filename, value)

    def __delitem__(self, key):
        filename = self._build_full_filename(key)
        os.remove(filename)

    def _generic_iter(self, iter_type: str):
        assert iter_type in {"keys", "values", "items"}
        walk_results = os.walk(self.base_dir)
        ext_len = len(self.file_type) + 1

        def splitter(path: str):
            result = []
            if path == ".":
                return result
            while True:
                head, tail = os.path.split(path)
                result = [tail] + result
                path = head
                if len(head) == 0:
                    break
            return result

        def step():
            for dir_name, _, files in walk_results:
                for f in files:
                    if f.endswith(self.file_type):
                        prefix_key = os.path.relpath(
                            dir_name, start=self.base_dir)

                        result_key = (*splitter(prefix_key), f[:-ext_len])

                        if iter_type == "keys":
                            yield result_key
                        elif iter_type == "values":
                            yield self[result_key]
                        else:
                            yield (result_key, self[result_key])

        return step()


