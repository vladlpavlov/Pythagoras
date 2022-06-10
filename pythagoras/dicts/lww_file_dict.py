import os
import pathlib
import pickle
import time
from typing import Any, Union

import jsonpickle

from pythagoras.persistent_dicts import SimpleDictKey, SimplePersistentDict


class LWWFileDirDict(SimplePersistentDict):
    """A persistent Dict that stores key-value pairs in local files.

    A new file is created for each key-value pair.
    A key is either a filename (without an extension),
    or a sequence of directory names that ends with a filename.
    A value can be any Python object, which is stored in a file.
    Insertion order is not preserved.

    FileDirDict can store objects in binary files (as pickles)
    or in human-readable text files (using jsonpickles).
    """

    def __init__(
        self,
        dir_name: Union[str, pathlib.Path] = "FileDirDict",
        file_type: str = "pkl",
        immutable_items: bool = False,
        retain_versions: int = 1,
    ):
        """A constructor defines location of the store and file format to use.

        dir_name is a directory that will contain all the files in
        the FileDirDict. If the directory does not exist, it will be created.

        file_type can take one of two values: "pkl" or "json".
        It defines which file format will be used by FileDirDict
        to store values.
        """

        super().__init__(immutable_items=immutable_items)

        self.file_type = file_type
        if isinstance(dir_name, pathlib.Path):
            self.base_dir = dir_name
        else:
            self.base_dir = pathlib.Path(dir_name).resolve()
        if retain_versions <= 0:
            raise ValueError("retain_versions must be larger than zero")
        self.retain_versions = retain_versions

        if not file_type in ("json", "pkl"):
            raise ValueError("file_type must be either pkl or json")

        if not self.base_dir.parent.exists():
            raise ValueError(f"Parent of {self.base_dir} does not exist")

        self.base_dir.mkdir(exist_ok=True)

    def __len__(self) -> int:
        """Get number of key-value pairs in the dictionary."""

        return len(list(self.base_dir.iterdir()))

    def mtimestamp(self, key: SimpleDictKey):
        return self._build_full_path(key).stat().st_mtime

    def clear(self):
        """Remove all elements form the dictionary."""

        assert (
            not self.immutable_items
        ), "Can't clear a dict that contains immutable items"

        for subdir in self.base_dir.iterdir():
            for data_file in subdir.iterdir():
                data_file.unlink()
            subdir.rmdir()

    def _make_data_name(self):
        return time.time()

    def _build_data_dir(self, key: SimpleDictKey):
        norm_key = self._normalize_key(key)
        return self.base_dir.joinpath("".join(norm_key))

    def _build_full_path(
        self,
        key: SimpleDictKey,
        create_subdirs: bool = False,
        new_value: bool = False,
    ) -> pathlib.Path:
        """Convert a key into a filesystem path."""
        data_dir = self._build_data_dir(key)

        if create_subdirs:
            data_dir.mkdir(exist_ok=True, parents=True)

        if new_value:
            timestamp = time.time()
            file_name = f"{timestamp}.{self.file_type}"
            return data_dir / file_name
        else:
            data_files = data_dir.iterdir()
            sorted_files = sorted(
                data_files,
                key=lambda file: file.stat().st_mtime,
                reverse=True,
            )

            # Collect garbage
            for garbage_file in sorted_files[self.retain_versions:]:
                garbage_file.unlink(missing_ok=True)

            return sorted_files[0]

    # TODO: add this method to the entire hierarchy of persistent dict classes
    def get_subdict(self, key: SimpleDictKey):
        """Get a subdictionary containing items with the same prefix_key."""
        full_dir_path = self._build_full_path(key, create_subdirs=True)
        return self.__class__(
            dir_name=full_dir_path,
            file_type=self.file_type,
            immutable_items=self.immutable_items,
        )

    def _read_from_file(self, data_file: pathlib.Path) -> Any:
        """Read a value from a file."""

        if self.file_type == "pkl":
            with data_file.open("rb") as fd:
                result = pickle.load(fd)
        elif self.file_type == "json":
            with data_file.open("r") as fd:
                result = jsonpickle.loads(fd.read())
        else:
            raise ValueError("file_type must be either pkl or json")

        return result

    def _save_to_file(self, data_file: pathlib.Path, value: Any) -> None:
        """Save a value to a file."""

        if self.file_type == "pkl":
            with data_file.open("wb") as f:
                pickle.dump(value, f)
        elif self.file_type == "json":
            with data_file.open("w") as f:
                f.write(jsonpickle.dumps(value, indent=4))
        else:
            raise ValueError("file_type must be either pkl or json")

    def __contains__(self, key: SimpleDictKey) -> bool:
        """True if the dictionary has the specified key, else False."""

        data_dir = self._build_data_dir(key)

        if not data_dir.exists():
            return False

        return next(data_dir.iterdir(), None) is not None

    def __getitem__(self, key: SimpleDictKey) -> Any:
        """Implementation for x[y] syntax."""

        if key not in self:
            raise KeyError(f"Key {key} does not exist")

        data_file = self._build_full_path(key)

        return self._read_from_file(data_file)

    def __setitem__(self, key: SimpleDictKey, value: Any):
        """Set self[key] to value."""

        data_file = self._build_full_path(key, create_subdirs=True, new_value=True)

        if data_file.parent.exists() and self.immutable_items:
            raise ValueError(f"Can not modify existing key: {key}")

        self._save_to_file(data_file, value)

    def __delitem__(self, key: SimpleDictKey) -> None:
        """Delete self[key]."""

        if self.immutable_items:
            raise ValueError("Can not modify persistent dict")

        data_dir = self._build_data_dir(key)

        if not data_dir.exists():
            raise KeyError(f"Key {key} does not exist")

        for data_file in data_dir.iterdir():
            data_file.unlink()

    def _generic_iter(self, iter_type: str):
        if iter_type not in ("keys", "values", "items"):
            raise ValueError(f"Invalid iter_type: {iter_type}")
        data_dirs = self.base_dir.iterdir()

        def step():
            for data_dir in data_dirs:
                if next(data_dir.iterdir(), None) is None:
                    continue

                prefix_key = data_dir.name
                result_key = self._remove_suffix_if_present(prefix_key)

                if iter_type == "keys":
                    yield result_key
                elif iter_type == "values":
                    yield self[result_key]
                else:
                    yield (
                        result_key,
                        self[result_key],
                    )

        return step()
