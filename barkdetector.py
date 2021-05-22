import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder

#from utils import get_messages_from_queue, download_wav_data, put_bark_metric

import librosa
import numpy as np
import json
import boto3
import os
import time
import uuid
import datetime
import warnings
import random
import sounddevice as sd

import barkcharts
warnings.filterwarnings("ignore")
#region = os.environ['AWS_DEFAULT_REGION']
#table_name = os.environ['TABLE_NAME']
#dynamodb = boto3.resource('dynamodb')
#table = dynamodb.Table(table_name)

# Label list
class_lables = [
    "air_conditioner",
    "car_horn",
    "children_playing",
    "dog_bark",
    "drilling",
    "engine_idling",
    "gunshot",
    "jackhammer",
    "siren",
    "street_music"
]

# load model
model = load_model('./model/weights.hdf5')

# Encode the classification labels
le = LabelEncoder()
y = np.array(class_lables)
yy = to_categorical(le.fit_transform(y))



def extract_feature(file_name):
    '''
    extract feature from file
    '''
    try:
        try:
            # Load file from a file
            audio_data, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
        except:
            # Take data from given data
            audio_data, sample_rate = file_name
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=40)
        mfccsscaled = np.mean(mfccs.T, axis=0)

    except Exception as e:
        print('Error encountered while parsing audio data: ',e)
        return None, None

    return np.array([mfccsscaled])


def return_prediction(file_name):
    # Extract features
    prediction_feature = extract_feature(file_name)
    # Predict vector
    predicted_vector = model.predict_classes(prediction_feature)
    # Predict class
    predicted_class = le.inverse_transform(predicted_vector)
    # Predict probability
    predicted_proba_vector = model.predict_proba(prediction_feature)
    predicted_proba = predicted_proba_vector[0]
    # Final guess
    prediction = {
        'class': predicted_class[0],
        'probabilities': {
            'air_conditioner': predicted_proba[0],
            'car_horn': predicted_proba[1],
            'children_playing': predicted_proba[2],
            'dog_bark': predicted_proba[3],
            'drilling': predicted_proba[4],
            'engine_idling': predicted_proba[5],
            'gunshot': predicted_proba[6],
            'jackhammer': predicted_proba[7],
            'siren': predicted_proba[8],
            'street_music': predicted_proba[9]
        }
    }
    return prediction

def process_file(file_name):
    # Get file info
    file_info = get_file_info(file_name)
    
    # Create bark dict
    barks = {}
    
    # List of barks
    barks['bark_list'] = []
    
    #Save the filename
    barks['filename'] = file_name
    # Date of file
    barks['date'] = file_info["datatime"].strftime("%Y-%m-%d")

    # Time of file
    barks['time'] = file_info["datatime"].strftime("%H:%M:%S")
    
    #
    barks['bark_chart']=''

    # Bark list offset, in seconds
    barks['bark_list_offset_seconds'] = []
    
    print("file: "+file_name)
    # Time offset of segment
    offset=0

    # Load file as a numpy array
    audio_data, sample_rate = librosa.load("detect/"+file_name, res_type='kaiser_fast')

    # Length of segment to be proccesed, in seconds
    segment_length = 4

    # Chop up the audio!
    audio_segments = [audio_data[i:i + sample_rate*segment_length] for i in range(0, len(audio_data), sample_rate*segment_length)]


    # Process each segment
    for audio_segment in audio_segments:
        barked = False
        # Make a prediction. We don't care about it unless it's a bark.
        prediction=int(return_prediction((audio_segment, sample_rate))["probabilities"]["dog_bark"]*100)
        '''
        if random.randint(0,40) == 10:
            sd.play(audio_segment, sample_rate)
            print('*',end='')
        '''
        # If it's a bark
        if prediction > 75:
            #print(f'{len(audio_segment)/sample_rate+offset} seconds \nDog barking percentage: %',prediction,'\n\n')
            print('1',end='')
            barks['bark_chart']+='1'
            barked = True
            # Time of bark
            time = offset
            # time = file_info["datatime"] + datetime.timedelta(seconds=offset)
            barks['bark_list_offset_seconds'] += [offset] #[time.strftime('%H:%M:%S')]
        else:
            print('0', end='')
            barks['bark_chart'] += '0'
        # Add the length of the segment to the offset
        offset += len(audio_segment)/sample_rate
    # Count up the barks
    barks['bark_count'] = len(barks['bark_list_offset_seconds'])
    return barks

def get_file_info(file_name):
    '''
    Just the time of creation
    '''
    _time = datetime.datetime.fromtimestamp(os.path.getmtime("detect/"+file_name))
    return {"datatime":_time}

def main():
    # Look in ./detect/
    for file in os.listdir('detect'):
        if file == ".gitignore":
            continue
        # Get the bark
        barks = process_file(file)
        # Move to the processed folder
        os.rename("detect/"+file, "detected/"+file)
        # Write the results to a JSON file
        with open("results/"+file.split('.')[0]+".json",'x') as FILE:
            json.dump(barks, FILE)
        print(f"\n{file} processed! {len(barks['bark_count'])} barks")
if __name__ == '__main__':
    main()
    barkcharts.main()
