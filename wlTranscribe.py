# Word-Level Transcription v1.7.0 - 2024-02-15
# got all the callbacks connected, just need to get a simple streamlit progress bar working based on it and im done with this
import sys
import streamlit as st
import os

st.write("Current working directory:", os.getcwd())
st.write("Directory contents:", os.listdir())
st.write("Python Path:", sys.path)

import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, text=True)
    st.write("FFmpeg version:", result.stdout)
except Exception as e:
    st.write("Error:", e)

# import pkg_resources
# for dist in pkg_resources.working_set:
#     st.write(dist.project_name, ":", dist.location)

import whisper_timestamped as whisper

import datetime
from deepmultilingualpunctuation import PunctuationModel
import os
import json
import base64
import datetime
import time
from tqdm import tqdm

from io import BytesIO
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from moviepy.editor import VideoFileClip, AudioFileClip


## STREAMLIT FUNCTIONS
def get_media_duration(file_path):
    if file_path.endswith((".mp3", ".m4a", ".wav", ".flac", ".aac")):
        with AudioFileClip(file_path) as audio:
            return audio.duration
    else:
        with VideoFileClip(file_path) as video:
            return video.duration


def format_duration(duration):
    minutes, seconds = divmod(duration, 60)
    return f"{int(minutes)}m {int(seconds)}s"


## FUNCTIONS
def dateTime(file_name):
    now = datetime.datetime.now()
    date_time_str = now.strftime("%y%m%d-%H%M")
    return f"{file_name}_{date_time_str}"


def toJson(dictionary, file_name):
    return json.dumps(dictionary, indent=4)


def toJson_OG(dictionary, file_name, prefix=""):
    if prefix != "":
        file_name_with_prefix = f"{prefix}_{file_name}"
        file_name = file_name_with_prefix
    file_name_with_date = dateTime(file_name)
    file_name_with_date += ".json"

    with open(file_name_with_date, "w") as file:
        result_json = json.dump(dictionary, file, indent=4)
    return result_json


class ProgressBar:
    def __init__(self, total, desc):
        self.pbar = tqdm(
            total=total,
            desc=desc,
            unit="frames",
            leave=False,
        )

    def update(self, increment):
        self.pbar.update(increment)

    def refresh(self, progress):
        self.pbar.n = progress
        self.pbar.refresh()

    def close(self):
        self.pbar.close()
        self.pbar = None

    def reset(self, total_reset):
        self.pbar.reset(total=total_reset)


use_tqdm = False
progress_bar = None

# * STREAMLIT SETUP
if "transcribe_initiated" not in st.session_state:
    st.session_state.transcribe_initiated = False

if "progress" not in st.session_state:
    st.session_state.progress = 0

if "transcribing_file" not in st.session_state:
    st.session_state.transcribing_file = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None


st.title("ModalMix Pro")
st.markdown("**Pre-Render Files for Auto-Assembly**")

uploaded_files = st.file_uploader(
    "Upload video or audio files or a zipped folder of files for transcription!",
    accept_multiple_files=True,
)

transcribe_button = st.button("Transcribe")

progress_length = None  # ? not sure I even need this


## CALLBACK FUNCTIONS FOR PROGRESS BAR AND ELAPSED TIMER
# called in ~/whisper/transcribe.py at line ~393
def update_variable(
    progress,
    stream=True,
    decode_increment=None,
    update=True,
    total_frames=None,
    description=None,
    reset=None,
):
    global progress_length  # ? make sure this doesn't need to be cleared before re-running - yeah pretty sure not needed (240222)
    if progress_length is None:

        if (
            total_frames is not None
        ):  # ? not sure I even need this if all the callback calls give relative percentages - yeah pretty sure not needed (240222)
            progress_length = total_frames

    if decode_increment == True:
        progress = progress + st.session_state.progress
    st.session_state.progress = progress

    st_progress_bar.progress(st.session_state.progress, text=description)

    if stream is not True:
        global progress_bar
        if progress_bar is None:
            if use_tqdm:
                progress_bar = ProgressBar(total=total_frames, desc=description)
        if reset is True:
            if use_tqdm:
                progress_bar.reset(progress)
            return
        if update is not False:
            if use_tqdm:
                progress_bar.update(progress)
        else:
            if use_tqdm:
                progress_bar.refresh(progress)


## CORE FUNCTIONS
def wlTranscribe(file_path):
    # print("\nTranscription begins...\n")
    audio = whisper.load_audio(file_path)
    model = whisper.load_model("medium", device="cpu")
    trans_base_dict = whisper.transcribe(
        model,
        audio,
        language="en",
        beam_size=5,
        best_of=5,
        temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        vad="auditok",
        callback=update_variable,
    )

    return trans_base_dict


def addPunct(text):
    model = PunctuationModel()
    result = model.restore_punctuation(text)
    return result


def process_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(
            ".mp4"
        ):  # You can adjust this to match the file types you are expecting
            file_path = os.path.join(folder_path, file)
            file_name = os.path.splitext(file)[0]

            print(f"Processing file: {file}")
            result = wlTranscribe(file_path)
            toJson(result, file_name, prefix="ASR")


## RUN FUCNCTIONS


# * STREAMLIT SETUP
def __streamlit_setup_folder():
    # Initialize session state variables for tracking transcription initiation

    # get estimated wait time
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
    return


# * TRANSCRIPTION PROCESS
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/5.1.mp4"  # (5 seconds)
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Full Proxies 240117/EXO_WM_S001_S001_T006_proxyWT.mp4"  # (3:52 minutes)
file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/EXO_WM_S001_S001_T004_proxyWT (1.5min) copy.mp4"  # (1.5 minutes)

# audio_folder = "/Users/tristangardner/Documents/Programming/3. Test Videos/Wayne Mayer/Full Proxies 240117"

if transcribe_button and uploaded_files and not st.session_state.transcribe_initiated:
    st.session_state.transcribe_initiated = True

    with tempfile.TemporaryDirectory() as temp_dir, BytesIO() as zip_buffer:
        with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zf:
            for i, uploaded_file in enumerate(uploaded_files):
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                file_duration = get_media_duration(temp_file_path)
                st.write(f"Estimated render time: {format_duration(file_duration)}")
                st_progress_bar = st.progress(
                    st.session_state.progress, text="Decoding..."
                )
                # st.session_state.start_time = time.time()
                # st.session_state.transcribing_file = True
                start_time = time.time()

                trans_result = wlTranscribe(temp_file_path)

                json_content = toJson(trans_result, os.path.basename(temp_file_path))

                zf.writestr(os.path.basename(temp_file_path) + ".json", json_content)

                end_time = time.time()
                execution_time = end_time - start_time
                execution_time = execution_time / 60
                execution_time = round(execution_time, 1)
                # st.session_state.transcribing_file = False
                # st.session_state.start_time = None
                st.write(f"\nThe script took {execution_time} minutes to complete.\n")

        zip_buffer.seek(0)
        st.download_button(
            "Download All Transcriptions",
            data=zip_buffer.getvalue(),
            file_name="transcriptions.zip",
            mime="application/zip",
        )

    # progress_bar.close()

    # print(f"\nThe script took {execution_time} minutes to complete.\n")


# #* Process time results
# 1.5 min file --process time--> 1.32 minutes
# 3.9 min file --process time--> 5.0 mintues
# 3.5 min file --process time--> 5.3 minutes
# 10.5 min file --process time--> 16.3 minutes
# 6.65 min file --process time--> __ minutes
