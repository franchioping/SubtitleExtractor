import fese

def extract_subs(file_path: str, language: str = 'en') -> list:
    video = fese.FFprobeVideoContainer(file_path)
    return video.copy_subtitles(filter(lambda sub: sub.language == language, video.get_subtitles()))


print(extract_subs('files/vid.mkv'))