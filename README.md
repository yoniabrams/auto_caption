# auto_caption
Exploring various methods in creating auto-caption pipelines for videos.

## Progress so far:
### Transcription process:
  - Explored the **PyTube** and **PyDub** APIs
  - Explored **PicoVoice's** Leopard model in conjunction with **MoviePy** / **ImageMagick**
    - *Blacktail tudio video* was a YouTube short, so it was vertical. Becaue of this, the subtitles went off the edge of the screen and this issue has to be fixed.
    - *Green Eggs and Ham* video was successful, though the transcription done by Leopard wasn't perfect. *(E.g. it said "Hale" in place of "Ham" once.)*
  - Implemented **HuggingFace's Distil-Whisper**, which was incridible at transcribing the first few seconds of the audio, but since I only used a small model I needed to then segment the complete audio to get a complete transcript.
    - *Audio Segmentation:* I did this using **pyAudioAnalysis.audioBasicIO** and **pyAudioAnalysis.audioSegmentation** which did a horrendous job segmenting the audio, and I eneded up with jibberish, even when trying lots of different sensitivies for the *"window"* and *"step"* parameters of the `.silence_removal()` method
### API / Application progress
  - Made a simple Gradio application with a very, very messy and non-pythonic implementation just for proof of concept.
  - Next, I will toy with **FastAPI**, ...
  - ... and eventually I will integrate into an existing **TelegramBot**
