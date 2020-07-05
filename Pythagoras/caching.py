from __future__ import annotations
import os, logging
import string, math
import shutil, numbers, time
import xxhash, pytest
from datetime import datetime
from typing import Optional, Callable, Any, Tuple, List, ClassVar
import pandas as pd
import types
from functools import wraps
from Pythagoras import NeatStr, LoggableObject, BasicStopwatch
from Pythagoras import TempAttributeAssignmentIfNotNone


class ReprBuilder(LoggableObject):
    """Base class for class representation factories."""

    glue_ch: str = ""
    div_ch: str = '__'
    eq_ch: str = '='
    left_bkt_ch: str = '('
    right_bkt_ch: str = ')'

    def __init__(self
                 , custom_handler: Optional[
                Callable[[Any, ReprBuilder], str]] = None
                 , *args
                 , **kwargs
                 ) -> None:
        super().__init__(*args, **kwargs)
        assert type(self) != ReprBuilder, (
            f"Class {type(self).__name__} can not be instantiated.")
        self.instance_defined_custom_handler = custom_handler

    REPR_BUILDERS = [
        "for_none"
        , "for_ellipsis"
        , "for_bool"
        , "for_numbers"
        , "for_str"
        , "for_dataframe"
        , "for_core_containers"
        , "for_custom_types"
        , "for_instance_defined_custom_types"
        , "for_all_others_types"
    ]

    def build_repr(self
                   , x: Any
                   , post_processor: Optional[Callable[[Any], str]] = None
                   ) -> Optional[str]:
        repr_str = None
        for b_name in self.REPR_BUILDERS:
            assert hasattr(self, b_name), f"{b_name} must be implemented"
            repr_builder = getattr(self, b_name)
            repr_str = repr_builder(x)
            if repr_str is None:
                continue
            if post_processor is not None:
                repr_str = post_processor(repr_str)
            break
        return repr_str

    # V-V-V-V-V-V-V-V-V-V-V---Virtual-Method---V-V-V-V-V-V-V-V-V-V-V-V-V-V
    def for_custom_types(self, _: Any) -> Optional[str]:
        """To be overloaded in child classes, if needed."""
        return None

    def for_instance_defined_custom_types(self, x: Any) -> Optional[str]:
        repr_str = None
        if self.instance_defined_custom_handler is not None:
            repr_str = (self.instance_defined_custom_handler)(x, self)
            assert isinstance(repr_str, str)
        return repr_str

    def for_none(self, x: Any) -> Optional[str]:
        if x is None:
            return "none"
        else:
            return None

    def for_ellipsis(self, x: Any) -> Optional[str]:
        if x is Ellipsis:
            return "dots"
        else:
            return None

    def for_bool(self, n: Any) -> Optional[str]:
        if isinstance(n, bool):
            repr_str = "bool"+self.glue_ch+("1" if n else "0")
        else:
            repr_str = None

        return repr_str

    def for_numbers(self, n: Any) -> Optional[str]:
        if isinstance(n, numbers.Integral):
            repr_str = "int" + self.glue_ch + str(n)
        elif isinstance(n, numbers.Real):
            repr_str = "real" + self.glue_ch + f"{n:.8g}"
        else:
            repr_str = None

        return repr_str

    def __str__(self) -> str:
        rez_str = type(self).__name__
        if self.instance_defined_custom_handler is not None:
            rez_str += (" with handler "
                        + self.instance_defined_custom_handler.__name__)
        else:
            rez_str += f" with no custom handler."
        return rez_str


class SlimReprBuilder(ReprBuilder):
    """Build concise, human-readable summary representations of objects."""

    def __init__(self
                 , *
                 , max_atomic_str_length=20
                 , custom_handler: Optional[Callable[
                [Any, SlimReprBuilder], str]] = None
                 , **kwargs
                 ) -> None:
        super().__init__(custom_handler=custom_handler, **kwargs)

        assert max_atomic_str_length in range(5, 50)
        self.max_atomic_str_length = max_atomic_str_length

    def __call__(self, *args, **kargs) -> str:
        repr_str = ""

        for a in args:
            repr_str += self.build_repr(a)
            repr_str += self.div_ch

        for k in kargs:
            repr_str += k
            repr_str += self.eq_ch
            repr_str += self.build_repr(kargs[k])
            repr_str += self.div_ch

        repr_str = repr_str.rstrip(self.div_ch)

        return repr_str

    def put_into_brackets(self, prefix: str, body: str,
                          suffix: str = "") -> str:
        return (str(prefix)
                + self.left_bkt_ch + str(body) + self.right_bkt_ch
                + str(suffix))

    def for_dataframe(self
                      , df: Any
                      , prefix: str = "dataframe"
                      , suffix: str = ""
                      ) -> Optional[str]:
        repr_str = None

        if isinstance(df, type(pd.DataFrame())):
            repr_str = f"{df.shape[0]}x{df.shape[1]}"
            n_nans = df.isna().sum().sum()
            if n_nans:
                repr_str += self.glue_ch + 'nans' + str(n_nans)
            repr_str = self.put_into_brackets(prefix, repr_str, suffix)

        return repr_str

    def for_str(self, s) -> Optional[str]:
        if not isinstance(s, str):
            return None

        if len(s) <= self.max_atomic_str_length:
            repr_str = "str" + self.glue_ch + s
        else:
            repr_str = self.put_into_brackets(
                prefix="str", body=str(len(s)))

        return repr_str

    def for_core_containers(self, c) -> Optional[str]:
        if isinstance(c, list):
            repr_str = self.put_into_brackets(
                prefix="list", body=str(len(c)))
        elif isinstance(c, set):
            repr_str = self.put_into_brackets(
                prefix="set", body=str(len(c)))
        elif isinstance(c, dict):
            repr_str = self.put_into_brackets(
                prefix="dict", body=str(len(c)))
        elif isinstance(c, tuple):
            repr_str = self.put_into_brackets(
                prefix="tuple", body=str(len(c)))
        else:
            repr_str = None

        return repr_str

    def for_all_others_types(self, x: Any) -> Optional[str]:
        if hasattr(x, "slim_repr") and callable(x.slim_repr):
            repr_str = x.slim_repr(self)
        else:
            repr_str = str(type(x).__qualname__)
            if hasattr(x, "__qualname__"):
                repr_str += '_' + x.__qualname__
            elif hasattr(x, "__name__"):
                repr_str += '_' + x.__name__
            self.warning(
                f"Building default type-based slim_repr <{repr_str}>"
                + f" for {repr(x)}.")

        return repr_str

    def __str__(self):
        rez_str = super().__str__().rstrip(".")
        rez_str += (
                f", special chars: "
                + self.left_bkt_ch + self.glue_ch + self.div_ch
                + self.eq_ch + self.right_bkt_ch
                + f" , cuts strings longer"
                + f" than {self.max_atomic_str_length} chars.")

        return rez_str


class FingerprintReprBuilder(ReprBuilder):
    """Build hash-based fingerprint representations of objects."""

    def __init__(self
                 , *
                 , hex_digest_length: int = 14
                 , custom_handler: Optional[Callable[
                [str, FingerprintReprBuilder], str]] = None
                 , **kwargs
                 ) -> None:
        super().__init__(custom_handler=custom_handler, **kwargs)
        assert hex_digest_length in range(5, 17)
        self.hex_digest_length = hex_digest_length

    def __call__(self, *args, **kwargs) -> str:
        digest_str = self.build_repr(
            x={"args": args, "kwargs": kwargs}
            , post_processor=self.fingerprint)

        short_digest_str = self.shorten_digest_str(digest_str)

        return short_digest_str

    def fingerprint(self, data) -> str:
        input_data = data

        if isinstance(input_data, str):
            input_data = input_data.encode()

        digest_str = xxhash.xxh64(input_data).hexdigest()

        return digest_str

    def shorten_digest_str(self
                           , digest_str: Optional[str]
                           ) -> Optional[str]:
        if digest_str is None:
            return None
        n_beginning = math.floor(self.hex_digest_length / 2)
        n_end = math.ceil(self.hex_digest_length / 2)
        short_digest_str = digest_str[:n_beginning] + digest_str[-n_end:]

        return short_digest_str

    def for_dataframe(self, df) -> Optional[str]:
        if not isinstance(df, type(pd.DataFrame())):
            return None

        values_digest_str = self.fingerprint(
            pd.util.hash_pandas_object(df, index=False).values)

        columns_digest_str = self.fingerprint(str(list(df.columns)))

        index_digest_str = self.fingerprint(str(list(df.index)))

        final_digest_str = self.fingerprint(
            values_digest_str + columns_digest_str + index_digest_str)

        return final_digest_str

    def for_dataframe_fast(self, df) -> Optional[str]:
        if not isinstance(df, type(pd.DataFrame())):
            return None

        srb = SlimReprBuilder()

        digest_str = srb(
            df
            , df.min().min(), df.min().mean(), df.min().max()
            , df.mean().min(), df.mean().mean(), df.mean().max()
            , df.max().min(), df.max().mean(), df.max().max())

        digest_str = self.fingerprint(digest_str)
        return digest_str

    def for_str(self, s) -> Optional[str]:
        if not isinstance(s, str):
            return None

        digest_str = type(s).__qualname__ + ' ' + str(len(s)) + ' '
        digest_str += s

        return digest_str

    def for_core_containers(self, c) -> Optional[str]:
        if isinstance(c, dict):
            digest_str = type(c).__qualname__ + ' ' + str(len(c)) + ' '
            for k in c:
                digest_str += self.build_repr(k) + ' '
                digest_str += self.build_repr(c[k]) + ' '
        elif isinstance(c, (list, set, tuple)):
            digest_str = type(c).__qualname__ + ' ' + str(len(c)) + ' '
            for i in c:
                digest_str += self.build_repr(i) + ' '
        else:
            digest_str = None

        return digest_str

    def for_all_others_types(self, x: Any) -> Optional[str]:
        if hasattr(x, "fingerprint_repr") and callable(x.fingerprint_repr):
            digest_str = x.fingerprint_repr(self)
        else:
            repr_str = str(type(x).__qualname__)
            if hasattr(x, "__qualname__"):
                repr_str += ', ' + x.__qualname__
            elif hasattr(x, "__name__"):
                repr_str += ', ' + x.__name__
            assert False, f"Can't create a hash digest for ({repr_str})"

        return digest_str

    def __str__(self) -> str:
        rez_str = super().__str__().rstrip(".")
        rez_str += f", digest len = {self.hex_digest_length} chars."
        return rez_str


class CacheFileWarden:
    """Abstract IO-backend for FileBasedCache"""

    def __init__(self) -> None:
        assert type(self) != CacheFileWarden, (
            f"Class {type(self).__name__} can not be instantiated.")

    @property
    def ext_str(self) -> str:
        """Filename extension for cache files that is used by this Warden."""
        assert False, "Not Implemented"
        return ""

    def read_dcs(self, file_name: str) -> Tuple[Any, float, str]:
        """Read dcs (Data, Cost_in_seconds, Source) from a file_name."""
        assert False, "Not Implemented"

    def write_dcs(self
                  , *
                  , data: Any
                  , file_name: str
                  , cost_in_seconds: float
                  , source: str) -> None:
        """Write dcs (Data, Cost_in_seconds, Source) to a file_name."""
        assert False, "Not Implemented"

    @property
    def max_file_name_len(self) -> int:
        """ Maximum supported length of a filename (path is not counted)."""
        return 250

    def replace_invalid_chars(self
                              , file_name: str
                              , replacement_ch: str = "_"
                              ) -> str:
        """Remove disallowed characters from a file_name string."""
        valid_chars = "~-_=.()<>" + string.ascii_letters + string.digits

        new_file_name = "".join(
            (c if c in valid_chars else replacement_ch) for c in file_name)

        return new_file_name

    def __str__(self) -> str:
        rez_str = type(self).__name__
        rez_str += (f" works with {self.ext_str} files,"
                    + f" names up to {self.max_file_name_len} chars long.")
        return rez_str


class PickleFileWarden(CacheFileWarden):
    """Pickle IO-backend for FileBasedCache."""

    @property
    def ext_str(self) -> str:
        """Filename extension for cache files that is used by this Warden."""
        return ".pkl"

    def read_dcs(self
                 , file_name: str
                 ) -> Tuple[Any, float, str]:
        """Read dcs (Data, Cost_in_seconds, Source) from a file_name."""
        result = pd.read_pickle(file_name)
        assert result["cost_in_seconds"] > 0
        assert isinstance(result["source"], str)
        return (result["data"], result["cost_in_seconds"], result["source"])

    def write_dcs(self
                  , *
                  , data: Any
                  , file_name: str
                  , cost_in_seconds: float
                  , source: str) -> None:
        """Write dcs (Data, Cost_in_seconds, Source) to a file_name."""
        assert cost_in_seconds > 0
        assert isinstance(source, str)
        package_to_write = {
            "data": data
            , "cost_in_seconds": cost_in_seconds
            , "source": source}
        pd.to_pickle(package_to_write, file_name)


class FileBasedCache(LoggableObject):
    """Generic file-based persistent cache manager."""

    def __init__(self
                 , *
                 , input_dir: str = "."
                 , cache_dir: str = "./FileBasedCache"
                 , slim_repr_builder: SlimReprBuilder = SlimReprBuilder()
                 , fingerprint_repr_builder: FingerprintReprBuilder = (
                    FingerprintReprBuilder())
                 , id_str: str = ""
                 , write_to_cache: bool = True
                 , read_from_cache: bool = True
                 , cache_file_warden: CacheFileWarden = PickleFileWarden()
                 , **kwargs
                 ) -> None:
        super().__init__(**kwargs)
        if not os.path.exists(cache_dir):
            self.warning(f"Creating new cache folder {cache_dir}. \n")
            os.makedirs(cache_dir)

        assert os.path.isdir(input_dir)
        assert os.path.isdir(cache_dir)
        assert cache_file_warden.max_file_name_len in range(50, 251)

        self.div_str = slim_repr_builder.div_ch
        self.input_dir = input_dir
        self.cache_dir = cache_dir
        self.slim_repr_builder = slim_repr_builder
        self.fingerprint_repr_builder = fingerprint_repr_builder
        self.id_str = id_str
        self.write_to_cache = write_to_cache
        self.read_from_cache = read_from_cache
        self.cache_file_warden = cache_file_warden

    def files_in_cache_dir(self) -> List[str]:
        """List full names of all the files from all the cache (sub)folders"""
        inside_cache_dir_list = []
        for (dir_path, _, file_names) in os.walk(self.cache_dir):
            inside_cache_dir_list += [os.path.join(dir_path, f)
                                      for f in file_names]

        return inside_cache_dir_list

    def files_in_input_dir(self) -> List[str]:
        """List full names of all the files from all the cache (sub)folders"""
        inside_input_dir_list = []
        for (dir_path, _, file_names) in os.walk(self.input_dir):
            inside_input_dir_list += [os.path.join(dir_path, f)
                                      for f in file_names]

        return inside_input_dir_list

    def limit_filename_length(self, old_filename: str) -> str:

        if len(old_filename) < self.cache_file_warden.max_file_name_len:
            return old_filename

        new_filename_tail = (
                "..." + self.div_str
                + self.fingerprint_repr_builder(old_filename))

        len_to_reuse = (
                self.cache_file_warden.max_file_name_len
                - len(new_filename_tail))

        new_filename = old_filename[:len_to_reuse] + new_filename_tail

        return new_filename

    def cache_dir_size(self) -> int:
        """Calculate the total size of all files in cache"""
        inside_cache_dir = self.files_in_cache_dir()
        total_cache_dir_size = sum(
            [os.path.getsize(name) for name in inside_cache_dir])
        return total_cache_dir_size

    def input_dir_size(self) -> int:
        """Calculate the total size of all files in input directory"""
        inside_input_dir = self.files_in_input_dir()
        total_input_dir_size = sum(
            [os.path.getsize(name) for name in inside_input_dir])
        return total_input_dir_size

    def cache_dir_len(self) -> int:
        """Calculate the total number of all files in cache"""
        inside_cache_dir = self.files_in_cache_dir()
        return len(inside_cache_dir)

    def input_dir_len(self) -> int:
        """Calculate the total number of all files in input directory"""
        inside_input_dir = self.files_in_input_dir()
        return len(inside_input_dir)

    def free_space(self) -> int:
        """Calculate an amount of free space available for caching"""
        available_space = shutil.disk_usage(self.cache_dir).free
        return available_space

    def __str__(self) -> str:
        """Create textual description of the cache object and its state."""
        description = (
                f"{type(self).__name__} in directory <{self.cache_dir}>"
                + f" contains {self.cache_dir_len()} files,"
                + f" with total size"
                + f" {NeatStr.mem_size(self.cache_dir_size())}. ")

        description += (f"There are {NeatStr.mem_size(self.free_space())}"
                        + f" of free space available in the directory. ")

        description += (f"Cache files are expected to have"
                        + f" <{self.cache_file_warden.ext_str}> extension. ")

        description += (f"Input files should be"
                        + f" located in <{self.input_dir}> folder,"
                        + f" which contains {self.input_dir_len()} files,"
                        + f" with total size"
                        + f" {NeatStr.mem_size(self.input_dir_size())}. ")

        if len(self.id_str) > 0:
            description += f"Cache ID is {self.id_str} . "

        if self.read_from_cache:
            description += (f"Cache READER is ACTIVE:"
                            + f" cached versions of objects are loaded from disk"
                            + f" if they are available there. ")
        else:
            description += (f"Cache READER is NOT active:"
                            + f" cached versions of objects are ignored. ")

        if self.write_to_cache:
            description += (f"Cache WRITER is ACTIVE: new objects"
                            + f" get saved to disk as they are created."
                            + f" Names of cache files can not be longer than"
                            + f" {self.cache_file_warden.max_file_name_len} characters. ")
        else:
            description += (f"Cache WRITER is NOT active: new objects"
                            + " do not get saved. ")

        description = description + super().__str__()

        return description

    def read_file(self
                  , input_file_name: str
                  , *
                  , file_reader_func: Callable[..., Any]
                  , read_from_cache: Optional[bool] = None
                  , write_to_cache: Optional[bool] = None
                  , **ka) -> Any:

        with TempAttributeAssignmentIfNotNone(
                self, "read_from_cache", read_from_cache):
            with TempAttributeAssignmentIfNotNone(
                    self, "write_to_cache", write_to_cache):
                result = self._read_file_impl(
                    input_file_name=input_file_name
                    , file_reader_func=file_reader_func
                    , **ka)

        return result

    def _read_file_impl(self
                        , input_file_name: str
                        , *
                        , file_reader_func: Callable[..., Any]
                        , **kwargs) -> Any:
        stopwatch = BasicStopwatch(start=True)
        sorted_kwargs = {k: kwargs[k] for k in sorted(kwargs.keys())}

        full_input_file_name = os.path.join(self.input_dir, input_file_name)
        assert os.path.isfile(full_input_file_name), (
                f"File {full_input_file_name} must exist"
                + f" if we want to read from it.")

        input_file_digest_builder = (
            type(self.fingerprint_repr_builder)(hex_digest_length=5))

        input_file_digest_str = input_file_digest_builder(input_file_name)

        subdir_name = (
                "Data" + self.div_str
                + input_file_name + self.div_str
                + input_file_digest_str)

        full_subdir_name = os.path.join(self.cache_dir, subdir_name)

        if os.path.exists(full_subdir_name):
            assert os.path.isdir(full_subdir_name), (
                f"{full_subdir_name} should be a directory")
        else:
            os.mkdir(full_subdir_name)

        input_file_size = os.path.getsize(full_input_file_name)
        if input_file_size == 0:
            self.warning(
                f"File {full_input_file_name} is empty (0 bytes in size) .")
        input_file_size_str = str(input_file_size)
        input_modif_time_str = datetime.fromtimestamp(
            os.path.getmtime(full_input_file_name)
        ).strftime('y%Y_m%m_d%d_h%H_m%M_s%S')

        if len(sorted_kwargs):
            extra_args_str = self.div_str
            extra_args_str += self.slim_repr_builder(**sorted_kwargs)
        else:
            extra_args_str = ""

        cache_file_name = (input_file_digest_str + self.div_str
                           + (self.id_str + self.div_str if len(
                    self.id_str) else '')
                           + 'size_' + input_file_size_str + self.div_str
                           + 'mtime_' + input_modif_time_str
                           + extra_args_str + self.div_str
                           + self.fingerprint_repr_builder(**sorted_kwargs)
                           )

        cache_file_name = self.limit_filename_length(cache_file_name)

        cache_file_name = self.cache_file_warden.replace_invalid_chars(
            cache_file_name)

        full_cache_file_name = os.path.join(
            full_subdir_name
            , cache_file_name + self.cache_file_warden.ext_str)

        if self.read_from_cache and os.path.exists(
                full_cache_file_name):
            (data, cost, source) = self.cache_file_warden.read_dcs(
                full_cache_file_name)
            stopwatch.stop_timer()
            new_cost = stopwatch.get_float_repr()
            message_str = ("Finished reading"
                           + f" {NeatStr.mem_size(os.path.getsize(full_cache_file_name))}"
                           + f" file {full_cache_file_name}."
                           + f" The process took {NeatStr.time_diff(new_cost)} now, while"
                           + f" in the past it costed {NeatStr.time_diff(cost)}"
                           + f" to read the same data from the original file {source}.\n")
            if new_cost >= cost:
                message_str = "Caching did not save time. " + message_str
                self.warning(message_str)
            else:
                self.info(message_str)

        else:
            stopwatch.reset_timer(start=True)
            data = file_reader_func(full_input_file_name, **kwargs)
            stopwatch.stop_timer()
            self.info("Finished reading "
                      + NeatStr.mem_size(
                os.path.getsize(full_input_file_name))
                      + f" file {full_input_file_name}."
                      + f" The process took {str(stopwatch)}.\n")
            if self.write_to_cache:
                self.cache_file_warden.write_dcs(
                    data=data
                    , file_name=full_cache_file_name
                    , cost_in_seconds=stopwatch.get_float_repr()
                    , source=full_input_file_name)
                self.info("Created "
                          + NeatStr.mem_size(
                    os.path.getsize(full_cache_file_name))
                          + f" file {full_cache_file_name}.\n")

        return data

    def read_csv(self
                 , input_file_name: str
                 , *
                 , read_from_cache: Optional[bool] = None
                 , write_to_cache: Optional[bool] = None
                 , **ka
                 ) -> pd.core.frame.DataFrame:
        """Read and return a Pandas DataFrame from a CSV file.

        The input file should be located in input_dir.
        When the function runs for the first time,
        it creates a cached version of the file and puts it to cache_dir.
        For the subsequent runs, the cached version is loaded instead of CSV,
        which speeds up the process. This behaviour can be altered
        by setting to False one or both of the OK flags in the __init__ method
        (read_from_cache and write_to_cache ).
        """
        assert input_file_name.endswith(".csv")
        data = self.read_file(
            input_file_name=input_file_name
            , read_from_cache=read_from_cache
            , write_to_cache=write_to_cache
            , file_reader_func=pd.read_csv
            , **ka)
        return data

    def get_generated_data(
            self
            , data_generator: Callable[..., Any]
            , *arguments
            , **kw_arguments
    ) -> Any:
        stopwatch = BasicStopwatch(start=True)
        func_digest_builder = type(
            self.fingerprint_repr_builder)(hex_digest_length=5)
        func_digest_str = func_digest_builder(
            getattr(data_generator, "__qualname__"))

        subdir_name = (
                "Func" + self.div_str + getattr(data_generator,
                                                "__qualname__")
                + self.div_str + func_digest_str)

        file_name = (
                func_digest_str + self.div_str
                + (self.id_str + self.div_str if len(self.id_str) else '')
                + self.slim_repr_builder(*arguments, **kw_arguments)
                + self.div_str
                + self.fingerprint_repr_builder(*arguments, **kw_arguments))

        file_name = self.limit_filename_length(file_name)
        file_name = self.cache_file_warden.replace_invalid_chars(file_name)

        full_subdir_name = os.path.join(self.cache_dir, subdir_name)

        if os.path.exists(full_subdir_name):
            assert os.path.isdir(full_subdir_name), (
                f"{full_subdir_name} should be a directory")
        else:
            os.mkdir(full_subdir_name)

        full_file_name = os.path.join(
            full_subdir_name, file_name + self.cache_file_warden.ext_str)

        if self.read_from_cache and os.path.exists(full_file_name):
            (data, cost, source) = self.cache_file_warden.read_dcs(
                full_file_name)
            stopwatch.stop_timer()
            new_cost = stopwatch.get_float_repr()
            message_str = ("Finished reading"
                           + f" {NeatStr.mem_size(os.path.getsize(full_file_name))}"
                           + f" file {full_file_name}."
                           + f" The process took {NeatStr.time_diff(new_cost)} now, while"
                           + f" in the past it costed {NeatStr.time_diff(cost)}"
                           + f" to generate the same data using function {source}().\n")
            if new_cost >= cost:
                message_str = "Caching did not save time. " + message_str
                self.warning(message_str)
            else:
                self.info(message_str)
        else:
            generator_repr = getattr(data_generator, "__qualname__")
            self.info(
                f"Starting generating data using {generator_repr}() ...")
            stopwatch.reset_timer(start=True)
            data = data_generator(*arguments, **kw_arguments)
            stopwatch.stop_timer()
            self.info(
                f"...finished generating data using {generator_repr}()."
                + f" The process took {str(stopwatch)}. \n")
            if data is None:
                self.warning(f" {generator_repr}() returned None.")

            if self.write_to_cache:
                self.cache_file_warden.write_dcs(
                    data=data
                    , file_name=full_file_name
                    , cost_in_seconds=stopwatch.get_float_repr()
                    , source=generator_repr)
                self.info("Created"
                          + f" {NeatStr.mem_size(os.path.getsize(full_file_name))}"
                          + f" file {full_file_name}.\n")

        return data

    def was_a_method_called(self, a_func, *func_args) -> bool:
        """ Check if a callable is a non-static (instance or class) method."""

        if not len(func_args):
            return False

        presumable_self = func_args[0]
        func_name = a_func.__name__

        if not hasattr(type(presumable_self), func_name):
            return False

        if not getattr(type(presumable_self),
                       func_name).__qualname__ == a_func.__qualname__:
            return False

        if not isinstance(getattr(presumable_self, func_name),
                          types.MethodType):
            return False

        return True

    def __call__(self
                 , a_function: Callable[..., Any]
                 ) -> Callable[..., Any]:
        """ Decoration magic happens here.

        __call__() is only supposed to be executed once,
        as part of decoration process.
        """

        @wraps(a_function)
        def wrapped_function(
                *args
                , read_from_cache: Optional[bool] = None
                , write_to_cache: Optional[bool] = None
                , **kwargs) -> Any:

            sorted_kwargs = {k: kwargs[k] for k in sorted(kwargs.keys())}

            if self.was_a_method_called(a_function, *args):
                if read_from_cache is None:
                    read_from_cache = getattr(
                        args[0], "read_from_cache", None)
                if write_to_cache is None:
                    write_to_cache = getattr(
                        args[0], "write_to_cache", None)

            with TempAttributeAssignmentIfNotNone(
                    self, "read_from_cache", read_from_cache):
                with TempAttributeAssignmentIfNotNone(
                        self, "write_to_cache", write_to_cache):
                    result = self.get_generated_data(
                        a_function, *args, **sorted_kwargs)

            return result

        return wrapped_function


class PickleCache(FileBasedCache):
    """Pickle-based persistent cache manager."""

    def __init__(
            self
            , *
            , input_dir: str = "."
            , cache_dir: str = "./PickleCache"
            , id_str: str = ""
            , write_to_cache: bool = True
            , read_from_cache: bool = True
            , custom_slim_repr_handler: Optional[Callable[
                [Any, SlimReprBuilder], Optional[str]]] = None
            , custom_fingerprint_repr_handler: Optional[Callable[
                [Any, FingerprintReprBuilder], Optional[str]]] = None
            , **kwargs
    ) -> None:
        super().__init__(
            input_dir=input_dir
            , cache_dir=cache_dir
            , id_str=id_str
            , write_to_cache=write_to_cache
            , read_from_cache=read_from_cache
            # -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
            , slim_repr_builder=SlimReprBuilder(
                custom_handler=custom_slim_repr_handler)
            , fingerprint_repr_builder=FingerprintReprBuilder(
                custom_handler=custom_fingerprint_repr_handler)
            , cache_file_warden=PickleFileWarden()
            , **kwargs
        )


class CacheableObject:
    """An abstract base class for cacheable containers and factories."""

    read_from_cache: Optional[bool] = None
    write_to_cache: Optional[bool] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert type(self) != CacheableObject, (
            f"Class {type(self).__name__} can not be instantiated.")

    # V-V-V-V-V-V-V-V-V-V-V---Virtual-Method---V-V-V-V-V-V-V-V-V-V-V-V-V-V-V
    def fingerpint_repr(self
                        , fprepr_builder: FingerprintReprBuilder
                        ) -> str:
        """Create ID string for the object to use for File Caching"""
        assert False, "Abstract method, must be overload in child classes."

    # V-V-V-V-V-V-V-V-V-V-V---Virtual-Method---V-V-V-V-V-V-V-V-V-V-V-V-V-V-V
    def slim_repr(self
                  , srepr_builder: SlimReprBuilder
                  ) -> str:
        """Create human-readable object summary to use for File Caching"""
        assert False, "Abstract method, must be overload in child classes."
