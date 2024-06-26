from functools import partial

import watchfiles
from pathlib import Path
import hashlib
from typing import TypedDict
import xxhash
import subs
import pickle
import json
import os
import logging

from config import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("SubtitleExtractor.log"),
        logging.StreamHandler()
    ]
)



class FileWatcher:
    def __init__(self):
        self.processed_video_last_updated_times = {}
        self.video_subtitles_map = {}

    def check_files(self):
        files: list[Path] = filter(
            lambda path: path.is_file(),
            MEDIA_PATH.rglob('*.mkv')
        )

        changed = []
        seen = []
        for file in files:

            last_updated = os.path.getctime(str(file.absolute()))

            if file in self.processed_video_last_updated_times.keys():
                if self.processed_video_last_updated_times[file] == last_updated:
                    continue
                else:
                    changed.append(file)

            logging.info(f" [*] Processing {file}")
            sub_files = subs.extract_subs(str(file.absolute()))

            self.video_subtitles_map[file] = [Path(x) for x in list(sub_files.values())]  # type: ignore
            self.processed_video_last_updated_times[file] = last_updated
            seen.append(file)

            self.save()
            logging.info(f"     - Extracted Subs ({len(list(sub_files.values()))}): {sub_files.values()}")

        logging.info("Clearing unused subs")
        for file in self.processed_video_last_updated_times.keys():
            if file not in seen:
                logging.info(f" [*] File {file} was removed, deleting subtitles")

                for sub_file in self.video_subtitles_map[file]:

                    if [x for xs in list(self.video_subtitles_map.values()) for x in xs].count(sub_file) == 1:
                        logging.info(f"      - Deleted {sub_file}")
                        sub_file.unlink()

                self.video_subtitles_map[file] = []

                if file in self.processed_video_last_updated_times:
                    self.processed_video_last_updated_times.remove(file)

    def save(self):
        with open(SAVEFILE, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls):
        if Path(SAVEFILE).exists():
            with open(SAVEFILE, "rb") as f:
                return pickle.load(f)
        return cls()


def main():
    if Path(LOCKFILE).exists():
        logging.warning("program is already running")
        return -1
    open(LOCKFILE, "w").close()
    watcher = FileWatcher.load()
    watcher.check_files()
    watcher.save()
    Path(LOCKFILE).unlink()


if __name__ == "__main__":
    try:
        logging.info("Starting Program")
        main()
    except Exception as e:
        logging.error(f"Exception {e}, Terminating")
        Path(LOCKFILE).unlink()
    except KeyboardInterrupt:
        logging.error("Keyboard Interrupt, Terminating")
        Path(LOCKFILE).unlink()
