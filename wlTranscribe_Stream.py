# ## Needs fixing 2024-02-06

""" ## streamlit callback session state practice
import streamlit as st

st.title("Let's explore session states and callback functions")

if "even_counter" and "odd_counter" not in st.session_state:
    st.session_state["even_counter"] = 2
    st.session_state["odd_counter"] = 1

increase_button = st.button("Add")
if increase_button:
    st.session_state["even_counter"] += 2
    st.session_state["odd_counter"] += 2

st.write(f"Number even_counter: {st.session_state['even_counter']}")
st.write(f"Number odd_counter: {st.session_state['odd_counter']}")


def reset_counter():
    if st.session_state["counter_to_reset"]:
        if st.session_state["counter_to_reset"] == "even_counter":
            st.session_state["even_counter"] = 2
        else:
            st.session_state["odd_counter"] = 1


counter_to_reset = st.radio(
    "Which to reset?",
    ["even_counter", "odd_counter"],
    on_change=reset_counter,
    key="counter_to_reset",
)

# st.write(st.session_state) 
"""

import streamlit as st
import time

st.title("Let's explore progress bars and callback functions")

if "progress_bar" not in st.session_state:
    st.session_state["progress"] = 0

progress_bar = st.progress(st.session_state["progress"])


def progress_callback(progress):
    st.session_state["progress"] = progress
    progress_bar.progress(st.session_state["progress"])


def long_function():
    for i in range(10):
        progress_callback((i + 1) / 10)
        time.sleep(1)


run_button = st.button("Run")

if run_button:
    if "progress" not in st.session_state:
        st.session_state["progress"] = 0
    long_function()

# from io import BytesIO
# import streamlit as st
# import os
# import tempfile
# import json
# from datetime import datetime

# # from moviepy.editor import VideoFileClip
# import whisper_timestamped as whisper
# from zipfile import ZipFile, ZIP_DEFLATED


# def streamlit_progress_callback(progress):
#     st.session_state.progress = progress
#     # Trigger a rerun to update the progress bar
#     # st.experimental_rerun()


# def wlTranscribe(file_path, progess_callback=None):
#     audio = whisper.load_audio(file_path)
#     model = whisper.load_model("medium", device="cpu")
#     trans_base_dict = whisper.transcribe(
#         model,
#         audio,
#         language="en",
#         beam_size=5,
#         best_of=5,
#         temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
#         vad="auditok",
#         progress_callback=progress_callback,
#     )
#     return trans_base_dict


# def toJson(dictionary, file_name):
#     return json.dumps(dictionary, indent=4)


# def get_video_duration(file_path):
#     # with VideoFileClip(file_path) as video:
#     return 1


# def format_duration(seconds):
#     hours, remainder = divmod(seconds, 3600)
#     minutes, seconds = divmod(remainder, 60)
#     return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"


# # Initialize session state variables for tracking transcription initiation
# if "transcribe_initiated" not in st.session_state:
#     st.session_state.transcribe_initiated = False

# if "progress" not in st.session_state:
#     st.session_state.progress = 0


# st.title("ModalMix Pro")
# st.markdown("**Pre-Render Files for Auto-Assembly**")

# uploaded_files = st.file_uploader(
#     "Upload video or audio files or a zipped folder of files for transcription!",
#     accept_multiple_files=True,
# )

# if uploaded_files and not st.session_state.transcribe_initiated:
#     with tempfile.TemporaryDirectory() as temp_dir:
#         total_duration_seconds = 0
#         for uploaded_file in uploaded_files:
#             temp_file_path = os.path.join(temp_dir, uploaded_file.name)
#             with open(temp_file_path, "wb") as f:
#                 f.write(uploaded_file.getbuffer())
#             total_duration_seconds += get_video_duration(temp_file_path)

#     st.write(
#         f"Estimated total wait time for all files: {format_duration(total_duration_seconds)}"
#     )

# transcribe_button = st.button("Transcribe All")

# if transcribe_button and uploaded_files and not st.session_state.transcribe_initiated:
#     st.session_state.transcribe_initiated = True
#     num_files = len(uploaded_files)
#     progress_bar_file = st.progress(st.session_state.progress)
#     progress_bar = st.progress(0)

#     with tempfile.TemporaryDirectory() as temp_dir, BytesIO() as zip_buffer:
#         with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zf:
#             for i, uploaded_file in enumerate(uploaded_files):
#                 st.session_state.progress = 0
#                 temp_file_path = os.path.join(temp_dir, uploaded_file.name)
#                 with open(temp_file_path, "wb") as f:
#                     f.write(uploaded_file.getbuffer())

#                 trans_result = wlTranscribe(
#                     temp_file_path, progress_callback=streamlit_progress_callback
#                 )
#                 json_content = toJson(trans_result, os.path.basename(temp_file_path))
#                 zf.writestr(os.path.basename(temp_file_path) + ".json", json_content)

#                 # Update progress bar for each file processed
#                 progress_bar.progress((i + 1) / num_files)

#         zip_buffer.seek(0)
#         st.download_button(
#             "Download All Transcriptions",
#             data=zip_buffer.getvalue(),
#             file_name="transcriptions.zip",
#             mime="application/zip",
#         )

#     # Optionally, allow resetting the transcription process to start over
#     if st.button("Reset"):
#         st.session_state.transcribe_initiated = False
#         progress_bar.empty()  # Optionally clear the progress bar after reset
