import string

allowed_key_chars = set(string.ascii_letters + string.digits + "()_-.=")
""" a set of characters allowd in Persistent Dict kes, filenames / S3 objectnames, and hash addresses"""