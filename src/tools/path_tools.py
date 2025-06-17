import shutil
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


def get_writable_db_path(db_name: str, db_dir: str = "resources/database") -> str:
    """
    Ensure there's a writable copy of the database file in the user's local app data directory.
    If it's not there, copy it from the bundled resources.
    :param db_name: The name of the database file.
    :param db_dir: The directory where the database file is located in the bundled resources.
    :returns: The path to the writable database file.
    """
    target_dir = get_app_root()
    db_path = os.path.join(target_dir, db_dir, db_name)

    if not os.path.exists(db_path):
        # If the database file doesn't exist in the target directory, copy it from the bundled resources
        bundled_db_path = os.path.join(get_app_root(), f"{db_dir}/{db_name}")

        if not os.path.exists(bundled_db_path):
            raise FileNotFoundError(f"Bundled database file not found: {bundled_db_path}")

        shutil.copyfile(bundled_db_path, db_path)

    return db_path
