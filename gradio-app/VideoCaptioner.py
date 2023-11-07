from VideoTranscriber import VideoTranscriber
import cv2

class VideoCaptioner(VideoTranscriber):
    def overlay_captions(self, video_output='captioned_video.mp4'):
        if not self.transcript:
            print("You need to transcribe the video first.")
            return
        if not self.audio_filepath:
            print("You need to specify a valid video source and download the video first.")
            return
        try:
            cap = cv2.VideoCapture(self.audio_filepath)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_output, fourcc, 30, (int(cap.get(3)), int(cap.get(4)))

            idx = 0
            for i, segment in enumerate(self.transcript):
                start_time = float(segment["start_time"])
            end_time = float(segment["end_time"])
            text = segment["text"]
            frame_rate = 30  # Adjust this if needed

            while idx < int(end_time * frame_rate):
                ret, frame = cap.read()
                if not ret:
                    break

                if int(start_time * frame_rate) <= idx:
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.6
                    font_color = (255, 255, 255)
                    line_type = 2

                    cv2.putText(frame, text, (50, 50), font, font_scale, font_color, line_type)

                out.write(frame)
                idx += 1

            cap.release()
            out.release()
            print(f"Captions added to {video_output}")
        except Exception as e:
            print(f"Error adding captions to the video: {e}")




def get_transcript(video_source):
    transcriber = VideoTranscriber(video_source)
    transcriber.download_video()
    transcriber.transcribe_video()
    transcriber.save_transcript_to_srt()
    return transcriber.get_srt_filepath()
