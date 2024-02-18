#!/Users/tristangardner/Documents/Programming/1. Apps - WIP/wordLevelTranscription/venv/bin/python3

## Word-Level Transcription v1.7.0 - 2024-02-15

## got all the callbacks connected, just need to get a simple streamlit progress bar working based on it and im done with this

import whisper_timestamped as whisper
import datetime
from deepmultilingualpunctuation import PunctuationModel
import os
import json
import base64
import datetime
import time
from tqdm import tqdm

# import streamlit as st
# import time
# import whisper
# from whisper.transcribe import global_progress
# import threading


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


##! 240217 working to polish the progress callback logic
""" 
1.5 min file --process time--> 1.32 minutes
3.9 min file --process time--> 5.0 mintues 

There are _ code blocks that contribute to wait time in a 1.5 min file

(1) Total frames are printed/stored
(2) The progress bar is initiated
(3) ** 1st decoding process is initiated
(4) segments compiled 
(5) ** 2nd decoding process is initiated
(6) segments compiled
(7) transcription complete
(8) ** word-alignment starts - custom progress initiated on whisper_segments
(9) Writes to josn 
(10) Script complete

What I want to do:
+ Check a 3 min file, how many decodes does it do? 
    ** results: 3.5 min file decodes many times, native progress bar seemed to suffice
- get tqdm values and Update progress bar after each decode/transcribe loop completes like tqdm 
- Update progress bar for word-alignment (easy)
- Display complete status 
- Move on to next file

"""


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
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/5.1.mp4"  # (5 seconds)
# file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Full Proxies 240117/EXO_WM_S001_S001_T006_proxyWT.mp4"  # (3:52 minutes)
file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/Wayne Mayer/Test Transcription Snippets/EXO_WM_S001_S001_T004_proxyWT (1.5min) copy.mp4"  # (1.5 minutes)


# audio_folder = "/Users/tristangardner/Documents/Programming/3. Test Videos/Wayne Mayer/Full Proxies 240117"


start_time = time.time()

dictioanry_result = wlTranscribe(file_path)

# update_variable()

toJson(dictioanry_result, file_path, prefix="")

progress_bar.close()

end_time = time.time()
execution_time = end_time - start_time
execution_time = execution_time / 60
execution_time = round(execution_time, 1)

# print(f"\nThe script took {execution_time} minutes to complete.\n")


## for a folder of files (working 2415)
""" def multiWrite(dictionary, file_name, prefix="transcription"):
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


## to make this executable from the terminal with a filepath as a parameter
""" To execute your script from the terminal with a variable as a filepath for the parameter of the main function, you can use command line arguments. In Python, you can access command line arguments via the `sys.argv` list. 

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
