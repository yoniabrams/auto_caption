import gradio as gr
# from VideoTranscriber import VideoTranscriber


# temporary imports:
import pvleopard
access_key = r'WrPIFvgrehYkFxNhizR0bM2lifz9mf/sbXGAX0cZPxsNjMRk4KZt1w=='
leopard = pvleopard.create(access_key=access_key)
from pytube import YouTube
import os
from sequence import Sequence

os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
assert os.getenv("IMAGEMAGICK_BINARY") is not None
magick_binary = r'C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe'
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": magick_binary})

from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.VideoClip import TextClip


def caption_video(video_url):
    # YouTube --> audio_file
    youtube = YouTube(video_url)
    audio_stream = youtube \
        .streams \
        .filter(only_audio=True, audio_codec='opus') \
        .order_by('bitrate') \
        .last()
    audio_filename = 'test_basic_gradio_transcriber_app.mp4'
    audio_stream.download(filename=audio_filename)

    # process the audio file using leopard:
    transcript, words = leopard.process_file(audio_filename)

    def second_to_timecode(x: float) -> str:
        hour, x = divmod(x, 3600)  # calculate hours
        minute, x = divmod(x, 60)  # calculate minutes
        second, x = divmod(x, 1)  # calculate seconds
        millisecond = int(x * 1000.)  # calculate milliseconds

        # format the timecode in HH:MM:SS,mmm format
        return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)

    # Function to convert a list of words into SRT format with specified parameters
    def to_srt(
            words: Sequence(pvleopard.Leopard.Word),
            endpoint_sec=1.,
            length_limit=16) -> str:

        # Helper function to create a section and add it to the result
        def _helper(end: int) -> None:
            lines.append("%d" % section)  # add ection number
            lines.append(
                "%s --> %s" %  # add time range in SRT format
                (
                    second_to_timecode(words[start].start_sec),
                    second_to_timecode(words[end].end_sec)
                )
            )
            lines.append(' '.join(x.word for x in words[start:(end + 1)]))  # combine words in section
            lines.append('')  # add an empty line to separate sections

        lines = list()  # initialize a list to store SRT lines
        section = 0  # initialize section number
        start = 0  # initialize start idx of the current section

        # iterate through the words to split them into sections
        for k in range(1, len(words)):
            # check for the amount of silence between words to see if the length limit is reached
            if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                    (length_limit is not None and (k - start) >= length_limit):
                _helper(k - 1)  # create a section and add it to the result
                start = k  # update start idx
                section += 1  # increment the section number

        _helper(len(words) - 1)  # create the final section

        # return the SRT-formatted transcript by joining the lines with line breaks
        return '\n'.join(lines)

    def save_subtitles(
            words: Sequence(pvleopard.Leopard.Word),
            subtitle_path):

        with open(subtitle_path, 'w') as srt_file:
            srt_file.write(to_srt(words))

    subtitle_filename = 'subtitles_for_testing_gradio_app.srt'
    save_subtitles(words, subtitle_filename)

    def make_textclip(txt):
        return TextClip(
            txt,
            font="Georgia-Bold",
            fontsize=30,  ##TODO - Change this to be based on the file-size
            color="blue",
            stroke_color="black",
            stroke_width=1,
        )

    # import video stream from youtube object
    video_stream = youtube \
        .streams \
        .filter(file_extension='mp4', progressive=True) \
        .get_highest_resolution()

    # download video without subtitles
    video_without_subtitles_filename = 'testing_gradio_video_no_subtitles.mp4'
    video_stream.download(filename=video_without_subtitles_filename)

    # load video into moviepy.editor.VideoFileClip object
    video = VideoFileClip(video_without_subtitles_filename)

    # Load the subtitles
    subtitles = SubtitlesClip(subtitle_filename, make_textclip=make_textclip)

    # Set the position and duration of the subtitles
    subtitles = subtitles \
        .set_position(("center", "bottom")) \
        .set_duration(video.duration)

    # Composite the video and subtitles
    final_clip = CompositeVideoClip([video, subtitles])

    # Write the final clip to a video file
    video_filename = 'testing_gradio_video_subtitles.mp4'
    final_clip.write_videofile(video_filename, fps=24, codec="libx264")

    return video_filename


# Create a Gradio interface
caption_video_interface = gr.Interface(
    fn=caption_video,
    inputs='text',
    outputs=gr.Video(label='With Subtitles')
)


if __name__ == '__main__':
    # DEMO.launch(show_api=False)

    caption_video_interface.launch()
