"""Verify the first authenticated Python contact with ElevenLabs TTS."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
OUTPUT_FILE = PROJECT_ROOT / "output" / "first-contact.mp3"
TEST_TEXT = "Voice Agent Integration Lab. Python first contact successful."
TTS_MODEL = "eleven_multilingual_v2"
OUTPUT_FORMAT = "mp3_44100_128"


def fail(message: str, exit_code: int) -> int:
    """Report a non-sensitive failure and return its process exit code."""
    print(message, file=sys.stderr)
    return exit_code


def main() -> int:
    load_dotenv(dotenv_path=ENV_FILE, override=False)
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()

    if not api_key:
        return fail(
            "Missing local API key: set ELEVENLABS_API_KEY in the root .env file.",
            1,
        )

    try:
        client = ElevenLabs(api_key=api_key)
        voices_response = client.voices.get_all()
    except Exception as exc:
        return fail(
            f"Authentication/API failure ({type(exc).__name__}).",
            2,
        )

    voices = voices_response.voices
    if not voices:
        return fail("Authentication succeeded, but no available voice was found.", 2)

    voice = voices[0]
    voice_name = voice.name or "Unnamed voice"

    try:
        audio_chunks = client.text_to_speech.convert(
            voice_id=voice.voice_id,
            text=TEST_TEXT,
            model_id=TTS_MODEL,
            output_format=OUTPUT_FORMAT,
        )
        audio_bytes = b"".join(audio_chunks)
    except Exception as exc:
        return fail(f"TTS generation failure ({type(exc).__name__}).", 3)

    if not audio_bytes:
        return fail("TTS generation failure: ElevenLabs returned empty audio.", 3)

    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_bytes(audio_bytes)
    except OSError as exc:
        return fail(f"File write failure ({type(exc).__name__}).", 4)

    print("ElevenLabs first contact succeeded.")
    print(f"Voice: {voice_name} ({voice.voice_id})")
    print(f"Model: {TTS_MODEL}")
    print(f"Output: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Bytes: {len(audio_bytes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
