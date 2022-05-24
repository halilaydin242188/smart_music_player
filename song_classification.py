from statistics import mode
from tracemalloc import start
import numpy as np
import math
import librosa
import keras
import time

genres = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]

def getMfcc(filepath, num_mfcc=13, n_fft=2048, hop_length=512, num_segments=10):
    SAMPLE_RATE = 22050
    TRACK_DURATION = 30
    SAMPLES_PER_TRACK = SAMPLE_RATE * TRACK_DURATION

    data = {
        "mfcc": []
    }

    samples_per_segment = int(SAMPLES_PER_TRACK / num_segments)
    num_mfcc_vectors_per_segment = math.ceil(samples_per_segment / hop_length)

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
    """
        if filepath[-3:] == "mp3":
            song = AudioSegment.from_mp3(filepath)
            song = AudioSegment.export(filepath, format="mp3")
    """

    model = keras.models.load_model("./ml_model/model_classification")

    test_data = np.array(getMfcc(filepath)) # test_data = (10, 130, 13) , should be (130, 13)
    test_data = test_data[..., np.newaxis] # test_data.shape = (10, 130, 13, 1)
    prediction = model.predict(test_data)
    predicted_index = np.argmax(prediction, axis=1)
    predicted_genre_index = mode(predicted_index)
    predicted_genre = genres[predicted_genre_index]

    return predicted_genre
