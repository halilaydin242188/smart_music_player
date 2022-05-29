import json
import os
import math
import librosa
import pydub
import numpy as np
from sklearn.model_selection import train_test_split
import keras as keras
import matplotlib.pyplot as plt
import tensorflow as tf
from statistics import mode

def load(filepath):
    sound = pydub.AudioSegment.from_file(filepath)
    sound = sound.set_channels(1) # to mono audio
    sound = sound.set_frame_rate(22050)
    y = np.array(sound.get_array_of_samples()).astype(np.float32)
    y = y / (1 << 8*2 - 1)  # normalization. AudioSegment use int16, so the max value is  `1 << 8*2 - 1`.

    return y, sound.frame_rate
      
def getMfcc(filepath, num_mfcc=13, n_fft=2048, hop_length=512, num_segments=10):
    SAMPLE_RATE = 22050
    TRACK_DURATION = 30
    SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION

    data = {
        "mfcc": []
    }

    samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)

    signal, sample_rate = load(filepath)


    for d in range(num_segments):
            
        start = samples_per_segment * d
        finish = start + samples_per_segment

        mfcc = librosa.feature.mfcc(signal[start:finish], sample_rate, n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
        mfcc = mfcc.T

        if len(mfcc) == num_mfcc_vectors_per_segment:
            data["mfcc"].append(mfcc.tolist())


    return data["mfcc"]

def predict(filepath):
    """
    if filepath[-3:] == "mp3":
        song = AudioSegment.from_mp3(filepath)
        song = AudioSegment.export(filepath, format="mp3")
    """
    
    model = keras.models.load_model("./model_pydub")

    test_data = np.array(getMfcc(filepath)) # test_data = (10, 130, 13) , should be (130, 13)
    test_data = test_data[..., np.newaxis] # test_data.shape = (10, 130, 13, 1)

    prediction = model.predict(test_data)

    predicted_index = np.argmax(prediction, axis=1)

    print("Predicted label: {}".format(predicted_index))

    print("RESULT : ", mode(predicted_index))



if __name__ == "__main__":

    filepath = r"datasets\GTZAN Dataset - Music Genre Classification\genres_original\rock\rock.00031.wav"
    predict(filepath)
