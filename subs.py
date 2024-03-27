import fese


def extract_subs(file_path: str, language: str = 'en') -> dict:
    video = fese.FFprobeVideoContainer(file_path)
    return video.copy_subtitles(filter(lambda sub: sub.language == language, video.get_subtitles()))

