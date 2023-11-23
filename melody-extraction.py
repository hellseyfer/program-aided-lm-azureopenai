import crepe
from scipy.io import wavfile

sr, audio = wavfile.read('sample_wav_acapella.wav')
# Perform melody extraction on a frame of audio
time, frequency, confidence, activation = crepe.predict(audio, sr)

print(time, frequency)