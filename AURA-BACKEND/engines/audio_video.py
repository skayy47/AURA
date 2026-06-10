"""Audio and video processing engine — transcription, features, frame extraction."""

from __future__ import annotations

from utils.helpers import get_logger

logger = get_logger(__name__)


def transcribe_audio(audio_file_path: str, model_size: str = "base") -> dict:
    """
    Transcribe audio using OpenAI Whisper.

    Returns {"text": str, "language": str, "duration_s": float}
    """
    import whisper  # type: ignore[import]

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_file_path)
    return {
        "text": result["text"],
        "language": result.get("language", "unknown"),
        "duration_s": round(result.get("duration", 0), 2),
    }


def extract_audio_features(audio_file_path: str) -> dict:
    """
    Extract audio features using librosa.

    Returns tempo, spectral centroid mean, MFCCs (first 5), duration.
    """
    import librosa  # type: ignore[import]

    y, sr = librosa.load(audio_file_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=5).mean(axis=1).tolist()
    return {
        "tempo_bpm": round(float(tempo), 2),
        "spectral_centroid_hz": round(float(centroid), 2),
        "mfccs": [round(m, 4) for m in mfccs],
        "duration_s": round(float(len(y) / sr), 2),
        "sample_rate": sr,
    }


def extract_frames_from_video(video_file_path: str, n_frames: int = 6) -> list:
    """
    Sample *n_frames* evenly-spaced frames from a video using OpenCV.

    Returns a list of BGR numpy arrays.
    """
    import cv2  # type: ignore[import]
    import numpy as np

    cap = cv2.VideoCapture(video_file_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, total - 1, n_frames, dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames
