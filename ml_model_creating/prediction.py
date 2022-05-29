from statistics import mode
import numpy as np
import keras
from pydub import AudioSegment

import mymodule


def predict(filepath):
    """
    if filepath[-3:] == "mp3":
        song = AudioSegment.from_mp3(filepath)
        song = AudioSegment.export(filepath, format="mp3")
    """
    
    model = keras.models.load_model("./ml_model/model_classification")

    test_data = np.array(mymodule.getMfcc(filepath)) # test_data = (10, 130, 13) , should be (130, 13)
    test_data = test_data[..., np.newaxis] # test_data.shape = (10, 130, 13, 1)

    prediction = model.predict(test_data)

    predicted_index = np.argmax(prediction, axis=1)

    print("Predicted label: {}".format(predicted_index))

    print("RESULT : ", mode(predicted_index))

filepath = "C:/Users/halil/Desktop/m\u00fcziklerim/Alan Walker - Fade.mp3"
predict(filepath)