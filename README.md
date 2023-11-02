# auto_caption
Exploring various methods in creating auto-caption pipelines for videos.

## Progress so far:
- Explored the **PyTube** and **PyDub** APIs
- Explored **PicoVoice's** Leopard model in conjunction with **MoviePy** / **ImageMagick**
  - *Blacktail tudio video* was a YouTube short, so it was vertical. Becaue of this, the subtitles went off the edge of the screen and this issue has to be fixed.
  - *Green Eggs and Ham* video was successful, though the transcription done by Leopard wasn't perfect. *(E.g. it said "Hale" in place of "Ham" once.)*
