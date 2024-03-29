## Word-Level Transcription v1.6.0 - 2024-01-25

import whisper_timestamped as whisper
import datetime
from deepmultilingualpunctuation import PunctuationModel
import os
import json
import base64
import datetime

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


## CORE FUNCTIONS
def wlTranscribe(file_path):
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
    )

    return trans_base_dict


from deepmultilingualpunctuation import PunctuationModel


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
file_path = "/Users/tristangardner/Documents/Programming/3. Test Media/CNEXT - Accelerate/Proxies/WSA0031_Proxy.mov"
audio_folder = "/Users/tristangardner/Documents/Programming/3. Test Videos/Wayne Mayer/Full Proxies 240117"

dictioanry_result = wlTranscribe(file_path)
toJson(dictioanry_result, file_path, prefix="")


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


multiWrite(dictionary_result, file_path, prefix="")
