import os

def platform_path(is_linux, *args):
    if (is_linux):
        return "/".join(args)
    else:
        return os.path.join(*args)
    
def platform_relpath(is_linux, *args):
    if (is_linux):
        return os.path.relpath(*args)
    else:
        return os.path.relpath(*args).replace("\\", "/")