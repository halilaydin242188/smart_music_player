from statistics import mode
import numpy as np
import math
import librosa
import keras
import pydub
import time
import os

genres = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]
model = None

def load(filepath): # https://github.com/librosa/librosa/issues/946
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


    if filepath[-3:] == "mp3":
        signal, sample_rate = load(filepath)
        
    else:
        signal, sample_rate = librosa.load(filepath, sr=SAMPLE_RATE)

    for d in range(num_segments):
            
        start = samples_per_segment * d
        finish = start + samples_per_segment

        mfcc = librosa.feature.mfcc(y=signal[start:finish], sr=sample_rate, n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
        mfcc = mfcc.T

        if len(mfcc) == num_mfcc_vectors_per_segment:
            data["mfcc"].append(mfcc.tolist())

    return data["mfcc"]

def get_song_genre(filepath):
    global model

    if model == None:
        model = keras.models.load_model("./ml_model_creating/model")

    test_data = np.array(getMfcc(filepath))
    test_data = test_data[..., np.newaxis]
    prediction = model.predict(test_data)
    predicted_index = np.argmax(prediction, axis=1)
    predicted_genre_index = mode(predicted_index)
    predicted_genre = genres[predicted_genre_index]

    return predicted_genre

# get_song_genre("C:/Users/halil/Desktop/test_musics/hiphop - 50 Cent - In Da Club (Official Music Video).mp3")