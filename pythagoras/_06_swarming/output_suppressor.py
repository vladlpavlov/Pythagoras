import os
import sys


class OutputSuppressor:
    def __init__(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr

    def __enter__(self):
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr