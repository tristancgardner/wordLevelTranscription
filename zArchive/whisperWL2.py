import json
import pandas as pd
import whisper_timestamped as whisper

audio = whisper.load_audio("Wayne_Test_E1C.mp4")

model = whisper.load_model("medium", device="cpu")

result = whisper.transcribe(model, audio, language="en")

transcript1 = json.dumps(result, indent = 2, ensure_ascii = False) 

with open("transcription.json", "w", encoding="utf-8") as file:
    file.write(transcript1)
    
with open("transcription.json", "r") as file: 
    data = json.load(file)
    
# text = []
start = []
end = []
confidence = []
words = []

for segment in data['segments']:
    for item in segment['words']:  # Assuming segment['words'] is a list of dictionaries
        words.append(item['text'])
        start.append(item['start'])
        end.append(item['end'])
        confidence.append(item['confidence'])


data_dict = {
    'Words' : words,
    'Start Time': start,
    'End Time': end,
}

file_name = "transcriptWL.json"
with open(file_name, 'w') as json_file:
    json.dump(data_dict, json_file)
    

def group_words_into_sentences_with_times(words, start_times, end_times):
    sentences = []
    sentence = []
    sentence_start_time = None

    for i, word in enumerate(words):
        word_detail = {
            "word": word,
            "start_time": start_times[i],
            "end_time": end_times[i]
        }
        if sentence_start_time is None:
            sentence_start_time = start_times[i]
        
        sentence.append(word_detail)

        # If a word ends with a punctuation mark that typically ends a sentence, group the words into a sentence
        if word.endswith(('.', '!', '?')):
            sentence_end_time = end_times[i]
            sentences.append({
                "sentence": " ".join([word_detail["word"] for word_detail in sentence]),
                "words": sentence,
                "start_time": sentence_start_time,
                "end_time": sentence_end_time
            })
            sentence = []
            sentence_start_time = None

    return sentences

# Extracting the words, start times, and end times from the JSON data
words = data_dict["Words"]
start_times = data_dict["Start Time"]
end_times = data_dict["End Time"]

# Grouping the words into sentences along with their individual and overall start and end times
enhanced_sentences = group_words_into_sentences_with_times(words, start_times, end_times)

# Adding the enhanced sentences data to the data_dict dictionary
data_dict['Sentences'] = enhanced_sentences

# Saving the enhanced transcription data to a new JSON file
with open('transcriptGrouped.json', 'w') as json_file:
    json.dump(data_dict, json_file)