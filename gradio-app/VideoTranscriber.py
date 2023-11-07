from pytube import YouTube
import moviepy.editor
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
# Distil-Whisper model id on hugging face api
model_id = "distil-whisper/distil-large-v2"
# load the model...
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,  # this helps keep loading time as low as possible
    use_safetensors=True  # use safetensors
)
model.to(device)
# ... and the processor
processor = AutoProcessor.from_pretrained(model_id)
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    torch_dtype=torch_dtype,
    device=device,
)


class VideoTranscriber:

    def __init__(self, video_source=None):
        self.video_source = video_source
        self.audio_filepath = None  # audio content of the video
        self.transcript = None
        self.srt_filepath = None  # transcript file

    def download_video(self, output_dir='.'):
        url_starters = set(['http', 'www.'])
        if self.video_source[:4] in url_starters:
            try:
                youtube = YouTube(self.video_source)
                stream = youtube.streams.filter(only_audio=True).first()
                self.audio_filepath = os.path.join(output_dir, f'{youtube.title}.mp3')
                stream.download(output_path=output_dir, filename=youtube.title)
                print(f"Downloaded audio to {self.audio_filepath}")
            except Exception as e:
                print(e)
        elif os.path.isfile(self.video_source):
            # create video file clip using moviepy
            video = moviepy.editor.VideoFileClip(self.video_source)
            # get audio from video
            audio = video.audio
            # build audio filename and write audio file
            video_name, video_ext = os.path.splitext(self.video_source)
            audio.write_audiofile(os.path.join(video_name, '.mp3'), codec='mp3')
        else:
            raise Exception

    def transcribe_video(self):
        if not self.audio_filepath:
            raise Exception

        try:
            audio_path = os.path.abspath(self.audio_filepath)
            self.transcript = pipe(audio_path)
            print("Transcription complete.")
        except Exception as e:
            print(f"Error transcribing video: {e}")

    def save_transcript_to_srt(self, output_file='transcript.srt'):
        if not self.transcript:
            print("You need to transcribe the video first.")
            return

        try:
            with open(output_file, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(self.transcript):
                    start_time = segment["start_time"]
                    end_time = segment["end_time"]
                    text = segment["text"]
                    srt_file.write(f"{i + 1}\n")
                    srt_file.write(f"{start_time} --> {end_time}\n")
                    srt_file.write(f"{text}\n\n")
            print(f"Transcript saved to {output_file}")
        except Exception as e:
            print(f"Error saving transcript to .srt file: {e}")

        self.srt_filepath = output_file

    def get_audio_filepath(self):
        return self.audio_filepath

    def get_srt_filepath(self):
        return self.srt_filepath

    def get_transcript(self):
        return self.transcript
