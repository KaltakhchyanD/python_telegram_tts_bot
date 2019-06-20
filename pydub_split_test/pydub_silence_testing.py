from pydub import AudioSegment
from pydub  import silence


wav_file = 'generated_audio_file.wav'


sorce_audiosegment = AudioSegment.from_wav(wav_file)

test = -22

other_temp = silence.detect_nonsilent(sorce_audiosegment, min_silence_len=100, silence_thresh=test)
silence_temp = silence.detect_silence(sorce_audiosegment, min_silence_len=100, silence_thresh=test)

temp_result = silence.split_on_silence(sorce_audiosegment, min_silence_len=100, silence_thresh=test)
print(f"Duration of segment - {len(sorce_audiosegment)}")
print(f"Len of gen list - {len(temp_result)}")

print(f"temp - {temp_result}")

print(f"other temp - {other_temp}")
print(f"silence - {silence_temp}")
print(f"Original rms - {sorce_audiosegment.rms}")

for index, segment in enumerate(temp_result):
    print(f'cycle {index}')
    segment.export('test_file_'+f"{index}"+'.wav', bitrate="48k", format="wav")