"""Chatterbox text-to-speech for manim-voiceover: narration cloned from a short sample of a real voice.

Runs offline on the GPU. Chatterbox lives in its own venv (.venv-chatterbox) because it needs numpy<2 and
torch 2.6, which clash with Manim. This service starts chatterbox_worker.py in that venv the first time a
line isn't already cached, and keeps it running for the rest of the render.

One-time setup on a new PC:
    python -m venv .venv-chatterbox
    .venv-chatterbox\\Scripts\\python.exe -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
    .venv-chatterbox\\Scripts\\python.exe -m pip install chatterbox-tts

Voice sample: voices/john_sample.wav (git-ignored, so the voice never lands in the public repo).
10-20 seconds of one person talking normally, quiet room, no music, no clipping.
"""
import atexit
import hashlib
import json
import subprocess
from pathlib import Path

from manim import logger
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service, path_to_string

ROOT = Path(__file__).parent
VENV_PYTHON = ROOT / ".venv-chatterbox" / "Scripts" / "python.exe"
WORKER = ROOT / "chatterbox_worker.py"


def _file_hash(path):
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()[:12]


class ChatterboxService(SpeechService):
    """SpeechService that speaks narration in a voice cloned from `sample_path`."""

    def __init__(self, sample_path, exaggeration=0.5, cfg_weight=0.5, temperature=0.8,
                 sentence_silence=0.35, seed=0, **kwargs):
        """
        Args:
            sample_path: WAV of the voice to clone (10-20 s of clean speech).
            exaggeration: emotion/intensity, 0.25-2.0. 0.5 is natural; higher is more animated and faster.
            cfg_weight: how tightly it follows the sample's delivery, 0-1. Lower (~0.3) slows the pace.
            temperature: randomness per take. Lower is steadier.
            sentence_silence: seconds of silence after each sentence.
            seed: change it to get a different take of every line.
        """
        initialize_speech_service(self, kwargs)
        self.sample_path = Path(sample_path)
        if not self.sample_path.exists():
            raise FileNotFoundError(f"Voice sample not found: {self.sample_path}")
        if not VENV_PYTHON.exists():
            raise FileNotFoundError(f"Chatterbox venv not found: {VENV_PYTHON} (see chatterbox_service.py)")
        self.sample_hash = _file_hash(self.sample_path)
        self.params = {"exaggeration": exaggeration, "cfg_weight": cfg_weight, "temperature": temperature,
                       "gap": sentence_silence, "seed": seed}
        self.proc = None

    def _worker(self):
        if self.proc is None or self.proc.poll() is not None:
            logger.info("Starting Chatterbox worker (first line takes ~20 s while the model loads)...")
            self.proc = subprocess.Popen([str(VENV_PYTHON), str(WORKER)], cwd=str(ROOT), text=True,
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)
            atexit.register(self._stop)
            ready = self.proc.stdout.readline()
            if not ready or not json.loads(ready).get("ready"):
                raise RuntimeError("Chatterbox worker failed to start; run it by hand to see the error "
                                   "(see chatterbox_worker.py docstring).")
        return self.proc

    def _stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        if cache_dir is None:
            cache_dir = self.cache_dir
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "chatterbox", "sample": self.sample_hash,
                      **self.params}

        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached

        audio_path = self.get_audio_basename(input_data) + ".wav" if path is None else path_to_string(path)
        request = {"text": input_text, "out": str((Path(cache_dir) / audio_path).resolve()),
                   "sample": str(self.sample_path.resolve()), **self.params}
        proc = self._worker()
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()
        reply = json.loads(proc.stdout.readline() or '{"ok": false, "error": "worker exited"}')
        if not reply.get("ok"):
            raise RuntimeError(f"Chatterbox failed on {input_text!r}: {reply.get('error')}")

        return {"input_text": text, "input_data": input_data, "original_audio": audio_path}
