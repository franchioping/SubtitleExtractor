import watchfiles
from pathlib import Path
import hashlib
from typing import TypedDict

import subs
import pickle
import json

from config import *


def sha256sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


VideoSubtitlesMapType = TypedDict('VideoSubtitlesMapType', {'video': Path, 'subs': list[Path]})


class FileWatcher:
    def __init__(self):
        self.processed_video_hashes = []
        self.video_subtitles_map: VideoSubtitlesMapType = {}

    def check_files(self):
        files: list[Path] = filter(
            lambda path: path.is_file(),
            MEDIA_PATH.rglob('*.mkv')
        )

        hashes_seen = []
        for file in files:
            file_hash = sha256sum(file)
            hashes_seen.append(file_hash)

            if file_hash in self.processed_video_hashes:
                continue

            print(f" [*] Processing {file}")
            sub_files = subs.extract_subs(str(file.absolute()))
            self.video_subtitles_map[file_hash] = [Path(x) for x in list(sub_files.values())]  # type: ignore
            self.processed_video_hashes.append(file_hash)
            self.save()
            print(f"     - Finished Extracting Subtitles")

        for file_hash in self.video_subtitles_map.keys():
            if file_hash not in hashes_seen:

                for sub_file in self.video_subtitles_map[file_hash]:  # type: ignore

                    if [x for xs in list(self.video_subtitles_map.values()) for x in xs].count(sub_file) == 1:
                        sub_file.unlink()

                self.video_subtitles_map[file_hash] = []  # type: ignore

                if file_hash in self.processed_video_hashes:
                    self.processed_video_hashes.remove(file_hash)

    def save(self):
        with open(SAVEFILE, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls):
        if Path(SAVEFILE).exists():
            with open(SAVEFILE, "rb") as f:
                return pickle.load(f)
        return cls()


if __name__ == "__main__":
    watcher = FileWatcher.load()
    watcher.check_files()
    watcher.save()
