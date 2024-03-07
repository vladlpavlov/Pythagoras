from persidict import PersiDict,FileDirDict

class OperationalHub:
    jason: PersiDict
    python: PersiDict
    text: PersiDict
    pickle: PersiDict

    def __init__(self, base_dir:str,**kwargs) -> None:
        self.jason = FileDirDict( file_type="json"
            ,dir_name = base_dir, digest_len=0, immutable_items=True)
        self.python = FileDirDict(file_type="py", base_class_for_values=str
            ,dir_name = base_dir, digest_len=0, immutable_items=True)
        self.text = FileDirDict( file_type="txt", base_class_for_values=str
            ,dir_name = base_dir, digest_len=0, immutable_items=True)
        self.binary = FileDirDict(file_type="pkl"
            ,dir_name = base_dir, digest_len=0, immutable_items=False)
