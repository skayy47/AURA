"""AURA — Page 5: Documents, Media & Export."""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from engines.ocr import load_pdf_to_text
from state.session import get_session
from utils.config import get_poppler_path
from utils.exporters import to_csv, to_excel, to_json, to_parquet
from utils.helpers import (
    get_logger,
    load_css,
    page_header,
    show_pipeline_progress,
    show_sidebar_status,
)

logger = get_logger(__name__)

st.set_page_config(page_title="AURA — Docs", page_icon="📄", layout="wide")
load_css()
show_pipeline_progress(5)

with st.sidebar:
    show_sidebar_status()

page_header("📄", "Documents & Export", "OCR · Audio · Video frames · Download cleaned data")

sess = get_session()

tab_export, tab_pdf, tab_av = st.tabs(["⬇ Export", "📄 PDF OCR", "🎵 Audio & Video"])

# ═════════════════════════════════════════════════════════════════
# Export
# ═════════════════════════════════════════════════════════════════
with tab_export:
    df = sess.cleaned_df if sess.cleaned_df is not None else sess.raw_df

    if df is None:
        st.markdown(
            """
<div style="background:#0E162E;border:1px solid rgba(90,60,200,0.4);
            border-radius:12px;padding:2rem;text-align:center;margin:1rem 0;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">📂</div>
  <div style="color:#94A3B8;font-size:0.9rem;">
    Load a dataset on the Ingest page to enable exports.</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_📂_Ingest.py", label="Go to Ingest →")
    else:
        source = "cleaned" if sess.cleaned_df is not None else "raw"
        st.markdown(
            f'<p style="font-size:0.82rem;color:#475569;margin-bottom:1rem;'
            f'font-family:monospace;">Exporting {source} dataset — '
            f'{df.shape[0]:,} rows · {df.shape[1]} cols</p>',
            unsafe_allow_html=True,
        )
        dl1, dl2, dl3, dl4 = st.columns(4)
        with dl1:
            st.download_button("⬇ CSV",     data=to_csv(df),     file_name="aura_export.csv",     mime="text/csv",             use_container_width=True)
        with dl2:
            st.download_button("⬇ Excel",   data=to_excel(df),   file_name="aura_export.xlsx",    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with dl3:
            st.download_button("⬇ JSON",    data=to_json(df),    file_name="aura_export.json",    mime="application/json",     use_container_width=True)
        with dl4:
            st.download_button("⬇ Parquet", data=to_parquet(df), file_name="aura_export.parquet", mime="application/octet-stream", use_container_width=True)

        if sess.cleaning_log:
            st.markdown(
                '<h3 style="color:#F1F5F9;font-size:0.95rem;font-weight:700;'
                'margin:1.5rem 0 0.6rem;">Cleaning Report</h3>',
                unsafe_allow_html=True,
            )
            for entry in sess.cleaning_log:
                step   = entry.get("step", "")
                detail = entry.get("detail", "")
                st.markdown(
                    f'<div style="color:#10B981;font-size:0.82rem;font-family:monospace;'
                    f'padding:2px 0;">▸ {step}: {detail}</div>',
                    unsafe_allow_html=True,
                )

# ═════════════════════════════════════════════════════════════════
# PDF OCR
# ═════════════════════════════════════════════════════════════════
with tab_pdf:
    st.markdown(
        '<h3 style="color:#F1F5F9;font-size:1rem;font-weight:700;'
        'margin-bottom:1rem;">PDF → Text (OCR)</h3>',
        unsafe_allow_html=True,
    )
    poppler_path = get_poppler_path()

    if not poppler_path:
        st.markdown(
            """
<div class="aura-card-elevated" style="border-color:rgba(245,158,11,0.4);">
  <strong style="color:#F59E0B;">⚙ POPPLER_PATH not configured</strong><br/>
  <span style="font-size:0.85rem;color:#94A3B8;">
    Add to your <code>.env</code> file:<br/>
    <code>POPPLER_PATH=C:\\path\\to\\poppler-25.11.0\\Library\\bin</code>
  </span>
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
                    sess.ocr_text = text
                except Exception as exc:
                    logger.exception("OCR error: %s", exc)
                    st.error(f"OCR failed: {exc}")
                    text = ""

            if text:
                m1, m2 = st.columns(2)
                m1.metric("Words",      len(text.split()))
                m2.metric("Characters", len(text))
                st.text_area("Extracted text", value=text, height=400)
                st.download_button(
                    "⬇ Download as .txt",
                    data=text.encode("utf-8"),
                    file_name=f"{Path(pdf_file.name).stem}_ocr.txt",
                    mime="text/plain",
                )
            else:
                st.warning("No text could be extracted from this PDF.")

# ═════════════════════════════════════════════════════════════════
# Audio & Video
# ═════════════════════════════════════════════════════════════════
with tab_av:
    st.markdown(
        '<h3 style="color:#F1F5F9;font-size:1rem;font-weight:700;'
        'margin-bottom:1rem;">Audio & Video Processing</h3>',
        unsafe_allow_html=True,
    )
    av_file = st.file_uploader(
        "Upload an audio or video file",
        type=["wav", "mp3", "mp4", "mov", "avi"],
        key="av_uploader",
    )

    if av_file is not None:
        suffix   = Path(av_file.name).suffix.lower()
        is_video = suffix in {".mp4", ".mov", ".avi"}

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(av_file.read())
            tmp_path = tmp.name

        try:
            sub_tabs = st.tabs(["🎙 Transcription", "📈 Audio features", "🎞 Video frames"])

        with sub_tabs[0]:
            model_size = st.selectbox("Whisper model size", ["tiny", "base", "small"], index=1)
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
                        st.error(f"Transcription failed: {exc}\n\nMake sure `openai-whisper` is installed.")

        with sub_tabs[1]:
            if st.button("Extract audio features", key="btn_features"):
                with st.spinner("Analysing with librosa…"):
                    try:
                        from engines.audio_video import extract_audio_features
                        feats = extract_audio_features(tmp_path)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Tempo (BPM)",              feats["tempo_bpm"])
                        m2.metric("Spectral centroid (Hz)",   feats["spectral_centroid_hz"])
                        m3.metric("Duration (s)",             feats["duration_s"])
                        st.write("**MFCCs (first 5):**", feats["mfccs"])
                    except Exception as exc:
                        logger.exception("Audio features error: %s", exc)
                        st.error(f"Feature extraction failed: {exc}\n\nMake sure `librosa` is installed.")

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
                                    frame_cols[i % 3].image(rgb, caption=f"Frame {i + 1}", use_container_width=True)
                            else:
                                st.warning("No frames could be extracted.")
                        except Exception as exc:
                            logger.exception("Frame extraction error: %s", exc)
                            st.error(f"Frame extraction failed: {exc}\n\nMake sure `opencv-python` is installed.")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

# ── Final CTA ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.success("🎉 You've explored all of AURA's features!")
st.page_link("app.py", label="← Back to Home", use_container_width=True)
