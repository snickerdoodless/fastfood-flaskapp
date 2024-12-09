import os
import re
import json
import platform
import subprocess

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".youtube_download_paths.json")
DEFAULT_PATH = os.path.join(os.path.expanduser("~"), "Downloads")

# PATH MANAGING UTILS
class DownloadPathManager:
    def __init__(self):
        self.paths = self.load_paths()

    def load_paths(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            return {"default": DEFAULT_PATH}
        except Exception as e:
            print(f"\n > Error Occurred: {e}")
            return {"default": DEFAULT_PATH}

    def save_paths(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.paths, f, indent=4)
        except Exception as e:
            print(f"Error Occurred: {e}")

    def add_paths(self):
        while True:
            new_path = input("\nEnter New Location: ").strip()
            if not self.is_valid(new_path):
                print("\n > ! Invalid Directory")
                continue

            if new_path in self.paths.values():
                print(f"\n > ! Location Exists: {new_path}")
            else:
                try:
                    os.makedirs(new_path, exist_ok=True)
                except Exception as e:
                    print(f"\n > ! Error Occurred: {e}")
                    continue

                self.paths[new_path] = new_path
                self.save_paths()
                print(f"\n > Success Adding: {new_path}")
                break

    def is_valid(self, path):
        # Directory format validation
        if os.name == "nt":  # Windows
            pattern = r"^[a-zA-Z]:\\(?:[^\\/:*?\"<>|\r\n]+\\?)*$"
        else:  # Unix-based
            pattern = r"^(/[^/ ]*)+/?$"

        if not re.match(pattern, path):
            return False

        try:
            testfile = os.path.join(path, "test.txt")
            with open(testfile, "w") as f:
                f.write("test")
            os.remove(testfile)
            return True
        except (TypeError, OSError):
            return False

def format_duration(seconds):
    if isinstance(seconds, str):
        return seconds

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes}:{remaining_seconds:02d}"

def is_valid_url(url):
    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$',
        re.IGNORECASE
    )
    return bool(youtube_regex.match(url))


def open_directory(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux and other Unix-based systems
            subprocess.run(["xdg-open", path])
    except Exception as e:
        raise OSError(f"Could not open directory: {e}")