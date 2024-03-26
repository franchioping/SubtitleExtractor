import fese

videopath = "./files/vid.mkv"

video = fese.FFprobeVideoContainer(videopath)

subtitles = video.get_subtitles()

print(subtitles[0].suffix)

extract = []
for subtitle in subtitles:
    if subtitle.language == "en":
        extract.append(subtitle)


print(video.copy_subtitles(extract))
