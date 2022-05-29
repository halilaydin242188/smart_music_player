import math
import librosa
import numpy as np

def getAllFeatures(filepath):

    classification_data = []

    mfcc_mean = []
    mfcc_var = []
    length = 66149

    signal, _ = librosa.load(filepath, duration=3)

    # CHROME STFT MEAN AND VAR
    c_stft = librosa.feature.chroma_stft(y=signal)
    c_stft = c_stft.reshape(-1)

    chroma_stft_mean = np.mean([c_stft])
    chroma_stft_var = np.var(c_stft)

    # RMS MEAN AND VAR
    rms = librosa.feature.rms(y=signal)

    rms_mean = np.mean(rms)
    rms_var = np.var(rms)

    # SPECTRAL CENTROİD MEAN AND VAR
    sc = librosa.feature.spectral_centroid(y=signal)

    spectral_centroid_mean = np.mean(sc)
    spectral_centroid_var = np.var(sc)

    # SPECTRAL BANDWİDTH MEAN AND VAR
    sb = librosa.feature.spectral_bandwidth(y=signal)

    spectral_bandwidth_mean = np.mean(sb)
    spectral_bandwidth_var = np.var(sb)

    # SPECTRAL ROLLOFF MEAN AND VAR
    ro = librosa.feature.spectral_rolloff(y=signal)

    rolloff_mean = np.mean(ro)
    rolloff_var = np.var(ro)

    # ZERO CROSSİNG RATE MEAN AND VAR
    zc = librosa.feature.zero_crossing_rate(y=signal)

    zero_crossing_rate_mean = np.mean(zc)
    zero_crossing_rate_var = np.var(zc)

    # HARMONY MEAN AND VAR
    h = librosa.effects.harmonic(y=signal)

    harmony_mean = np.mean(h)
    harmony_var = np.var(h)

    # HARMONY MEAN AND VAR
    p = librosa.effects.percussive(y=signal)

    perceptr_mean = np.mean(p)
    perceptr_var = np.var(p)

    # TEMPO
    tempo, _ = librosa.beat.beat_track(y=signal)

    # MFCC MEAN AND VARS
    mfcc20 = librosa.feature.mfcc(y=signal, n_mfcc=20)

    for i in range(0, 20):
        mfcc_mean.append(np.mean(mfcc20[i, :]))
        mfcc_var.append(np.var(mfcc20[i, :]))
    
    classification_data.append(length)
    classification_data.append(chroma_stft_mean)
    classification_data.append(chroma_stft_var)
    classification_data.append(rms_mean)
    classification_data.append(rms_var)
    classification_data.append(spectral_centroid_mean)
    classification_data.append(spectral_centroid_var)
    classification_data.append(spectral_bandwidth_mean)
    classification_data.append(spectral_bandwidth_var)
    classification_data.append(rolloff_mean)
    classification_data.append(rolloff_var)
    classification_data.append(zero_crossing_rate_mean)
    classification_data.append(zero_crossing_rate_var)
    classification_data.append(harmony_mean)
    classification_data.append(harmony_var)
    classification_data.append(perceptr_mean)
    classification_data.append(perceptr_var)
    classification_data.append(tempo)
    for i in range(0, 20):
        classification_data.append(mfcc_mean[i])
        classification_data.append(mfcc_var[i])

    #return  np.array(classification_data).reshape(1, -1)
    return classification_data

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

        mfcc = librosa.feature.mfcc(signal[start:finish], sample_rate, n_mfcc=num_mfcc, n_fft=n_fft, hop_length=hop_length)
        mfcc = mfcc.T

        if len(mfcc) == num_mfcc_vectors_per_segment:
            data["mfcc"].append(mfcc.tolist())


    return data["mfcc"]

    