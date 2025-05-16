import sys
import os

def get_app_root() -> str:
    """
    Get the root directory of the application.
    Works both during normal execution and when frozen with PyInstaller.
    :returns: The absolute path to the root directory.
    """
    if getattr(sys, 'frozen', False):
        # If the application is frozen (e.g., using PyInstaller)
        return sys._MEIPASS  # type: ignore
    else:
        # If the application is running in a normal Python environment
        return os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
