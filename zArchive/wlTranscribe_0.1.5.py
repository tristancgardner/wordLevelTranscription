#%%
import pandas as pd

from IPython.core.display import HTML
HTML("""
<style>
.dataframe td, .dataframe th {
    max-width: None;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: normal;
}
</style>
""")

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

#%%
import os 
import pandas as pd
import whisper_timestamped as whisper

# %%

def wlTranscribe (video_file_path):
    audio = whisper.load_audio(video_file_path)
    model = whisper.load_model("medium", device="cpu")
    trans_base_dict = whisper.transcribe(model, audio, language="en")
        
    start = []
    end = []
    confidence = []
    words = []

    for segment in trans_base_dict['segments']:
        for item in segment['words']:  # Assuming segment['words'] is a list of dictionaries
            words.append(item['text'])
            start.append(item['start'])
            end.append(item['end'])
            confidence.append(item['confidence'])

    trans_clean_dict = {
        'Words' : words,
        'Start Time' : start,
        'End Time': end,
    }

    return trans_clean_dict


#%%

folder_path = '/Users/tristangardner/Documents/Programming/Test Videos/WM_ACam_Proxies'

# Step 1: List and sort all video files in the folder
video_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.mp4' or '.mov' or '.wav' or '.m4a')])
transcriptions = []

# Step 2: Loop through video files and transcribe
for video_file in video_files:
    full_path = os.path.join(folder_path, video_file)
    transcription = wlTranscribe(full_path)  # Ensure wlTranscribe returns the transcription
    transcriptions.append(transcription)

# Step 3: Save results in DataFrame
df_master = pd.DataFrame({'Video_File': video_files, 'Transcription': transcriptions})

df_master

#%%
# Step 4: Convert DataFrame to a master dictionary
master_dict = {row['Video_File']: {'Transcription': row['Transcription']} for index, row in df_master.iterrows()}

master_dict

# %%
# Time to transcibe Wauyne Mayer ACam Proxies       8.0 minutes

df_master
