"""Chatterbox voice-cloning worker. Runs inside .venv-chatterbox, NOT the Manim environment.

Chatterbox needs torch 2.6 and numpy<2, which clash with Manim's numpy 2, so it lives in its own venv.
chatterbox_service.py starts this script once per render and keeps it running, so the model loads once.

Protocol: one JSON request per line on stdin, one JSON reply per line on stdout.
    request: {"text": ..., "out": "path.wav", "sample": "voice.wav", "exaggeration": .5,
              "cfg_weight": .5, "temperature": .8, "gap": .35, "seed": 0}
    reply:   {"ok": true, "duration": 3.2}  or  {"ok": false, "error": "..."}

Test by hand:
    .venv-chatterbox\\Scripts\\python.exe chatterbox_worker.py --say "Hello from APW." --sample voices\\john_sample.wav
"""
import argparse
import json
import re
import sys
import wave

# Libraries print progress to stdout; keep stdout clean for replies only.
REPLY = sys.stdout
sys.stdout = sys.stderr

import numpy as np  # noqa: E402
import torch  # noqa: E402
from chatterbox.tts import ChatterboxTTS  # noqa: E402

# Chatterbox drifts on long inputs (it was trained on clips up to ~40 s), so speak one sentence at a time.
SENTENCE_END = re.compile(r"(?<=[.!?;:])\s+")


def split_sentences(text):
    return [s.strip() for s in SENTENCE_END.split(text.strip()) if s.strip()]


def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[chatterbox] loading model on {device}...", flush=True)
    return ChatterboxTTS.from_pretrained(device=device)


def synthesize(model, req):
    pieces = []
    gap = np.zeros(int(model.sr * req.get("gap", 0.35)), dtype=np.float32)
    for i, sentence in enumerate(split_sentences(req["text"])):
        torch.manual_seed(req.get("seed", 0) + i)  # same text + seed -> same take
        wav = model.generate(sentence, audio_prompt_path=req["sample"],
                             exaggeration=req.get("exaggeration", 0.5),
                             cfg_weight=req.get("cfg_weight", 0.5),
                             temperature=req.get("temperature", 0.8))
        pieces += [wav.squeeze(0).cpu().numpy().astype(np.float32), gap]
    audio = np.concatenate(pieces) if pieces else gap
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    with wave.open(req["out"], "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(model.sr)
        wf.writeframes(pcm.tobytes())
    return len(pcm) / model.sr


def serve(model):
    REPLY.write(json.dumps({"ready": True}) + "\n")
    REPLY.flush()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = {"ok": True, "duration": synthesize(model, json.loads(line))}
        except Exception as e:  # report and keep serving
            reply = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        REPLY.write(json.dumps(reply) + "\n")
        REPLY.flush()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--say", help="speak this once and exit (for testing)")
    ap.add_argument("--sample", default="voices/john_sample.wav")
    ap.add_argument("--out", default="chatterbox_test.wav")
    ap.add_argument("--exaggeration", type=float, default=0.5)
    ap.add_argument("--cfg-weight", type=float, default=0.5)
    ap.add_argument("--gap", type=float, default=0.35)
    args = ap.parse_args()
    model = load_model()
    if args.say:
        d = synthesize(model, {"text": args.say, "out": args.out, "sample": args.sample,
                               "exaggeration": args.exaggeration, "cfg_weight": args.cfg_weight,
                               "gap": args.gap})
        print(f"[chatterbox] wrote {args.out} ({d:.1f} s)")
    else:
        serve(model)
