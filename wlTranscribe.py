# Word-Level Transcription v1.7.0 - 2024-02-15
# got all the callbacks connected, just need to get a simple streamlit progress bar working based on it and im done with this

import whisper_timestamped as whisper
import datetime
from deepmultilingualpunctuation import PunctuationModel
import os
import json
import base64
import datetime
import time
from tqdm import tqdm

import streamlit as st
from io import BytesIO
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from moviepy.editor import VideoFileClip


## STREAMLIT FUNCTIONS
""" def streamlit_progress_callback(progress):
    st.session_state.progress = progress
    # Trigger a rerun to update the progress bar
    # st.experimental_rerun()
 """


def get_video_duration(file_path):
    with VideoFileClip(file_path) as video:
        return 1


def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"


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


progress_bar = None


## CALLBACK FUNCTION FOR PROGRESS BAR
# called in ~/whisper/transcribe.py at line ~393
def update_variable(
    progress, update=True, total_frames=None, description=None, reset=None
):
    # If using TQDM in terminal
    global progress_bar
    if progress_bar is None:
        progress_bar = ProgressBar(total=total_frames, desc=description)
    if reset is True:
        progress_bar.reset(progress)
        return
    if update is not False:
        progress_bar.update(progress)
    else:
        progress_bar.refresh(progress)

    # If using Streamlit progress bar


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
""" st.title("ModalMix Pro")
st.markdown("**Pre-Render Files for Auto-Assembly**")

uploaded_files = st.file_uploader(
    "Upload video or audio files or a zipped folder of files for transcription!",
    accept_multiple_files=True,
)
 """

# * TRANSCRIPTION PROCESS
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/5.1.mp4"  # (5 seconds)
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Full Proxies 240117/EXO_WM_S001_S001_T006_proxyWT.mp4"  # (3:52 minutes)
file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/EXO_WM_S001_S001_T004_proxyWT (1.5min) copy.mp4"  # (1.5 minutes)

# audio_folder = "/Users/tristangardner/Documents/Programming/3. Test Videos/Wayne Mayer/Full Proxies 240117"


start_time = time.time()

dictioanry_result = wlTranscribe(file_path)

toJson(dictioanry_result, file_path, prefix="")

progress_bar.close()

end_time = time.time()
execution_time = end_time - start_time
execution_time = execution_time / 60
execution_time = round(execution_time, 1)

# print(f"\nThe script took {execution_time} minutes to complete.\n")


""" #* Process time results
1.5 min file --process time--> 1.32 minutes
3.9 min file --process time--> 5.0 mintues  
"""


""" #/ for a folder of files (working 2415)
def multiWrite(dictionary, file_name, prefix="transcription"):
    if prefix != "":
        file_name_with_prefix = f"{prefix}_{file_name}"
        file_name = file_name_with_prefix
    file_name_with_date = dateTime(file_name)
    file_name_with_date += ".txt"

    if dictionary["text"]:
        with open(file_name_with_date, "w") as file:
            file.write(dictionary["text"])

    return file_name_with_date


multiWrite(dictionary_result, file_path, prefix="") """


""" #/ to make this executable from the terminal with a filepath as a parameter


To execute your script from the terminal with a variable as a filepath for the parameter of the main function, you can use command line arguments. In Python, you can access command line arguments via the `sys.argv` list. 

Here's a basic example of how you can modify your script to accept a filepath as a command line argument:

```python
import sys

def main(filepath):
    # Your code here

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    main(filepath)
```

In this script, `sys.argv` is a list that contains the command line arguments that were passed to the script. `sys.argv[0]` is always the name of the script itself, `sys.argv[1]` is the first argument, and so on. 

You can run this script from the terminal and pass a filepath as a command line argument like this:

```bash
python script.py /path/to/file
```

Replace `script.py` with the name of your script and `/path/to/file` with the filepath you want to pass to the main function. """
