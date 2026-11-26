"""Piper text-to-speech for manim-voiceover: a free neural voice that runs on this PC, offline.

Voice models (.onnx plus .onnx.json) live in voices/, which is git-ignored. Download one with:

    python -m piper.download_voices --download-dir voices en_GB-northern_english_male-medium

Browse voices: https://rhasspy.github.io/piper-samples/
"""
import wave
from pathlib import Path

from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service, path_to_string


class PiperService(SpeechService):
    """SpeechService that renders narration with a local Piper voice model."""

    def __init__(self, model_path, length_scale=1.0, noise_scale=None, noise_w_scale=None,
                 sentence_silence=0.0, **kwargs):
        """
        Args:
            model_path: path to the voice's .onnx file (its .onnx.json must sit next to it).
            length_scale: how long each sound lasts; above 1.0 is slower. Much above 1.1 slurs words.
            noise_scale: variation in tone (None = the voice's default). Lower is steadier.
            noise_w_scale: variation in sound timing (None = the voice's default). Lower is crisper.
            sentence_silence: seconds of silence after each sentence (and at the end of the line).
        """
        from piper import PiperVoice  # imported here so other services work without piper installed

        initialize_speech_service(self, kwargs)
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Piper voice not found: {self.model_path}\n"
                f"Download it with: python -m piper.download_voices --download-dir voices {self.model_path.stem}")
        self.voice = PiperVoice.load(str(self.model_path))
        self.length_scale = length_scale
        self.noise_scale = noise_scale
        self.noise_w_scale = noise_w_scale
        self.sentence_silence = sentence_silence

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        from piper import SynthesisConfig

        if cache_dir is None:
            cache_dir = self.cache_dir
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "piper", "voice": self.model_path.stem,
                      "length_scale": self.length_scale, "noise_scale": self.noise_scale,
                      "noise_w_scale": self.noise_w_scale, "sentence_silence": self.sentence_silence}

        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = self.get_audio_basename(input_data) + ".wav" if path is None else path_to_string(path)
        config = SynthesisConfig(length_scale=self.length_scale, noise_scale=self.noise_scale,
                                 noise_w_scale=self.noise_w_scale)
        with wave.open(str(Path(cache_dir) / audio_path), "wb") as wf:
            first = True
            for chunk in self.voice.synthesize(input_text, syn_config=config):  # one chunk per sentence
                if first:
                    wf.setframerate(chunk.sample_rate)
                    wf.setsampwidth(chunk.sample_width)
                    wf.setnchannels(chunk.sample_channels)
                    first = False
                wf.writeframes(chunk.audio_int16_bytes)
                wf.writeframes(b"\x00\x00" * int(chunk.sample_rate * self.sentence_silence))

        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}
