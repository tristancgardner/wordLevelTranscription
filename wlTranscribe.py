# Word-Level Transcription v1.7.0 - 2024-03-03
# removing streamlit shit
import sys
import os


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
from moviepy.editor import AudioFileClip, VideoFileClip

sys.path.append(
    "D:\\Programming\\transcribeAuto\\wordLevelTranscription\\venv\\src\\whisper\\whisper"
)
import whisper_timestamped as whisper


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


def toJson(dictionary, file_name, prefix=""):
    if prefix != "":
        file_name_with_prefix = f"{prefix}_{file_name}"
        file_name = file_name_with_prefix
    file_name_with_date = dateTime(file_name)
    file_name_with_date += ".json"

    with open(file_name_with_date, "w") as file:
        json.dump(dictionary, file, indent=4)


class ProgressBar:
    def __init__(self, total, desc):
        self.pbar = tqdm(
            total=total,
            desc=desc,
            unit="frames",
            leave=False,
        )

    def update(self, increment, desc):
        self.pbar.update(increment)
        self.pbar.set_description(desc)

    def refresh(self, progress, desc):
        self.pbar.n = progress
        self.pbar.refresh()
        self.pbar.set_description(desc)

    def close(self):
        self.pbar.close()
        self.pbar = None

    def reset(self, total_reset):
        self.pbar.reset(total=total_reset)


use_tqdm = True
progress_bar = None
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
            progress_bar.update(progress, desc=description)
    else:
        if use_tqdm:
            progress_bar.refresh(progress, desc=description)


whisper_model = None


## CORE FUNCTIONS
def wlTranscribe(file_path):
    audio = whisper.load_audio(file_path)

    global whisper_model
    whisper_model = "medium"
    model = whisper.load_model(whisper_model, device="cuda")

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

## WINDOWS OS
file_list = [
    r"D:\Programming\transcribeAuto\Test Media\WM_0.067min.mp4",
    r"D:\Programming\transcribeAuto\Test Media\EXO_WM_S001_S001_T004_proxyWT_1.0min.mp4",
    r"D:\Programming\transcribeAuto\Test Media\Mod 7 - psychology tips_6.5min.m4a",
    r"D:\Programming\transcribeAuto\Test Media\Mod 5 - psychology examples_10.5min.m4a",
    r"D:\Programming\transcribeAuto\Test Media\EXO_WM_S001_S001_T014_proxyWT_5.75min.mp4",  # 5th
    r"D:\Programming\transcribeAuto\Test Media\Mod 7 - technology advancement examples_3.5min.m4a",
]
file_path = file_list[5]

test_media_folder = r"D:\Programming\transcribeAuto\Test Media"

if not os.path.exists(file_path):
    print(f"File does not exist: {file_path}")

## MAC_OS
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/5.1.mp4"  # (5 seconds)
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Full Proxies 240117/EXO_WM_S001_S001_T006_proxyWT.mp4"  # (3:52 minutes)
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/EXO_WM_S001_S001_T004_proxyWT (1.5min) copy.mp4"  # (1.5 minutes)

# audio_folder = "/Users/tristangardner/Documents/Programming/3. Test Videos/Wayne Mayer/Full Proxies 240117"

start_time = time.time()


#! if it's a folder, process all files in the folder
# if os.path.isdir(file_path):
#     process_folder(file_path)


trans_result = wlTranscribe(file_path)

# for path in sys.path: # debugs module import issues
#     print(path)

file_name = os.path.splitext(os.path.basename(file_path))[0]
toJson(trans_result, os.path.basename(file_name))
end_time = time.time()
execution_time = end_time - start_time
execution_time = execution_time / 60
execution_time = round(execution_time, 2)

print(f"\nThe script took {execution_time} minutes to complete.\n")


# get duration of file and print
duration = get_media_duration(file_path)
duration = format_duration(duration)


ptimes_file_path = os.path.join(os.getcwd(), "process_times.csv")

if not os.path.exists(ptimes_file_path):
    with open(ptimes_file_path, "w") as file:
        file.write("File, Duration, Process Time, Model\n")
        file.write(f"{file_path}, {duration}, {execution_time}, {whisper_model}\n")

else:
    with open(ptimes_file_path, "a") as file:
        file.write(f"{file_path}, {duration}, {execution_time}, {whisper_model}\n")
