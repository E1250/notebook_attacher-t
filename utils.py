import os

def platform_path(is_linux, *args):
    if (is_linux):
        return "/".join(args)
    else:
        return os.path.join(*args)