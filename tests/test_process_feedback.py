import importlib.util
import sys
from pathlib import Path


def load_process_feedback_module():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "process-feedback.py"
    spec = importlib.util.spec_from_file_location("process_feedback", str(script_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_process_once_with_audio(tmp_path):
    module = load_process_feedback_module()

    # Prepare fake unprocessed item
    fid = 12345
    item = {"id": fid, "hasAudio": True, "noteText": None}

    module.fetch_unprocessed = lambda base_url: [item]

    # Replace download_audio to write some bytes to the provided dest Path
    def fake_download_audio(base_url, feedback_id, dest: Path):
        assert feedback_id == fid
        dest.write_bytes(b"FAKEAUDIO")
        return True

    module.download_audio = fake_download_audio

    # Replace transcribe to return deterministic transcript
    def fake_transcribe(audio_path: Path, model_name: str, language: str):
        # Ensure the file exists and has the content we wrote
        assert audio_path.exists()
        return "hello test"

    module.transcribe = fake_transcribe

    # Capture patched transcripts
    patched = []

    def fake_patch_transcript(base_url, feedback_id, transcript):
        patched.append((feedback_id, transcript))

    module.patch_transcript = fake_patch_transcript

    handled = module.process_once("http://example.local", model_name="tiny", language="auto")
    assert handled == 1
    assert patched == [(fid, "hello test")]


def test_process_once_text_only():
    module = load_process_feedback_module()

    fid = 54321
    note = "This is a typed note"
    item = {"id": fid, "hasAudio": False, "noteText": note}

    module.fetch_unprocessed = lambda base_url: [item]

    patched = []

    def fake_patch_transcript(base_url, feedback_id, transcript):
        patched.append((feedback_id, transcript))

    module.patch_transcript = fake_patch_transcript

    handled = module.process_once("http://example.local", model_name="tiny", language="auto")
    assert handled == 1
    assert patched == [(fid, note)]
