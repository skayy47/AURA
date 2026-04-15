"""AURA — Page 5: Document Processing (OCR, Audio, Video)."""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from engines.ocr import load_pdf_to_text
from state.session import get_session
from utils.config import get_poppler_path
from utils.helpers import get_logger, show_page_header, show_pipeline_progress, show_sidebar_status

logger = get_logger(__name__)

st.set_page_config(page_title="AURA · Documents", page_icon="📄", layout="wide")


def inject_css() -> None:
    css_path = Path("assets/css/aura.css")
    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


inject_css()

session = get_session()
show_sidebar_status()
show_pipeline_progress(5)
show_page_header("📄", "Document Processing", "OCR, audio transcription, and video frame extraction")

tab_pdf, tab_av = st.tabs(["📄 PDF OCR", "🎵 Audio & Video"])

# =============================================================
# PDF OCR
# =============================================================
with tab_pdf:
    st.markdown("### PDF → Text (OCR)")
    poppler_path = get_poppler_path()

    if not poppler_path:
        st.markdown(
            """
<div class="aura-card" style="border-color:var(--color-warning);">
  <strong>⚙️ POPPLER_PATH not configured</strong><br/>
  Add the following to your <code>.env</code> file:<br/>
  <code>POPPLER_PATH=C:\\path\\to\\poppler-25.11.0\\Library\\bin</code>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        pdf_file = st.file_uploader("Upload a PDF", type=["pdf"], key="pdf_uploader")
        if pdf_file is not None:
            with st.spinner("Extracting text…"):
                try:
                    text = load_pdf_to_text(pdf_file, poppler_path)
                    session.ocr_text = text
                except Exception as exc:
                    logger.exception("OCR error: %s", exc)
                    st.error(f"OCR failed: {exc}")
                    text = ""

            if text:
                m1, m2 = st.columns(2)
                m1.metric("Words", len(text.split()))
                m2.metric("Characters", len(text))
                st.text_area("Extracted text", value=text, height=400)
                st.download_button(
                    "⬇️ Download as .txt",
                    data=text.encode("utf-8"),
                    file_name=f"{Path(pdf_file.name).stem}_ocr.txt",
                    mime="text/plain",
                )
            else:
                st.warning("No text could be extracted from this PDF.")

# =============================================================
# Audio & Video
# =============================================================
with tab_av:
    st.markdown("### Audio & Video processing")
    av_file = st.file_uploader(
        "Upload an audio or video file",
        type=["wav", "mp3", "mp4", "mov", "avi"],
        key="av_uploader",
    )

    if av_file is not None:
        suffix = Path(av_file.name).suffix.lower()
        is_video = suffix in {".mp4", ".mov", ".avi"}

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(av_file.read())
            tmp_path = tmp.name

        sub_tabs = st.tabs(["🎙 Transcription", "📈 Audio features", "🎞 Video frames"])

        with sub_tabs[0]:
            model_size = st.selectbox(
                "Whisper model size", ["tiny", "base", "small"], index=1
            )
            if st.button("Transcribe", key="btn_transcribe"):
                with st.spinner(f"Loading Whisper {model_size} model…"):
                    try:
                        from engines.audio_video import transcribe_audio

                        result = transcribe_audio(tmp_path, model_size)
                        st.metric("Language", result["language"])
                        st.metric("Duration (s)", result["duration_s"])
                        st.text_area("Transcript", value=result["text"], height=300)
                    except Exception as exc:
                        logger.exception("Transcription error: %s", exc)
                        st.error(
                            f"Transcription failed: {exc}\n\n"
                            "Make sure `openai-whisper` is installed."
                        )

        with sub_tabs[1]:
            if st.button("Extract audio features", key="btn_features"):
                with st.spinner("Analysing with librosa…"):
                    try:
                        from engines.audio_video import extract_audio_features

                        feats = extract_audio_features(tmp_path)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Tempo (BPM)", feats["tempo_bpm"])
                        m2.metric("Spectral centroid (Hz)", feats["spectral_centroid_hz"])
                        m3.metric("Duration (s)", feats["duration_s"])
                        st.write("**MFCCs (first 5):**", feats["mfccs"])
                    except Exception as exc:
                        logger.exception("Audio features error: %s", exc)
                        st.error(
                            f"Feature extraction failed: {exc}\n\n"
                            "Make sure `librosa` is installed."
                        )

        with sub_tabs[2]:
            if not is_video:
                st.info("Video frame extraction only works with .mp4, .mov, or .avi files.")
            else:
                n_frames = st.slider("Frames to extract", 2, 12, 6)
                if st.button("Extract frames", key="btn_frames"):
                    with st.spinner("Extracting frames with OpenCV…"):
                        try:
                            import cv2

                            from engines.audio_video import extract_frames_from_video

                            frames = extract_frames_from_video(tmp_path, n_frames)
                            if frames:
                                frame_cols = st.columns(min(3, len(frames)))
                                for i, frame in enumerate(frames):
                                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                    frame_cols[i % 3].image(
                                        rgb,
                                        caption=f"Frame {i + 1}",
                                        use_container_width=True,
                                    )
                            else:
                                st.warning("No frames could be extracted.")
                        except Exception as exc:
                            logger.exception("Frame extraction error: %s", exc)
                            st.error(
                                f"Frame extraction failed: {exc}\n\n"
                                "Make sure `opencv-python` is installed."
                            )
