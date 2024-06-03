# import argparse
# import os
# import numpy as np
# import speech_recognition as sr

# from datetime import datetime, timedelta
# from queue import Queue
# from time import sleep
# from sys import platform
# from transformers import TFWhisperForConditionalGeneration, WhisperProcessor
# import tensorflow as tf

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--model", default="medium", help="Model to use",
#                         choices=["tiny", "base", "small", "medium", "large"])
#     parser.add_argument("--non_english", action='store_true',
#                         help="Don't use the english model.")
#     parser.add_argument("--energy_threshold", default=1,
#                         help="Energy level for mic to detect.", type=int)
#     parser.add_argument("--record_timeout", default=40,
#                         help="How real time the recording is in seconds.", type=float)
#     parser.add_argument("--phrase_timeout", default=5,
#                         help="How much empty space between recordings before we "
#                              "consider it a new line in the transcription.", type=float)
#     if 'linux' in platform:
#         parser.add_argument("--default_microphone", default='pulse',
#                             help="Default microphone name for SpeechRecognition. "
#                                  "Run this with 'list' to view available Microphones.", type=str)
#     args = parser.parse_args()
#     # The last time a recording was retrieved from the queue.
#     phrase_time = None
#     # Thread safe Queue for passing data from the threaded recording callback.
#     data_queue = Queue()
#     # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
#     recorder = sr.Recognizer()
#     recorder.energy_threshold = args.energy_threshold
#     # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
#     recorder.dynamic_energy_threshold = False

#     # Important for linux users.
#     # Prevents permanent application hang and crash by using the wrong Microphone
#     # if 'linux' in platform:
#     #     mic_name = args.default_microphone
#     #     if not mic_name or mic_name == 'list':
#     #         print("Available microphone devices are: ")
#     #         for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     #             print(f"Microphone with name \"{name}\" found")
#     #         return
#     #     else:
#     #         for index, name in enumerate(sr.Microphone.list_microphone_names()):
#     #             if mic_name in name:
#     #                 source = sr.Microphone(
#     #                     sample_rate=16000, device_index=index)
#     #                 break
#     # else:
#     #     source = sr.Microphone(device_index= 1,sample_rate=16000)
#     source = sr.Microphone()

#     # Load / Download model
#     processor = WhisperProcessor.from_pretrained("openai/whisper-small")
#     audio_model = TFWhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

#     audio_model.config.forced_decoder_ids = processor.get_decoder_prompt_ids(language="en", task="transcribe")
#     record_timeout = args.record_timeout
#     phrase_timeout = args.phrase_timeout

#     transcription = ['']

#     with source:
#         recorder.adjust_for_ambient_noise(source)

#     def record_callback(recognizer, audio: sr.AudioData) -> None:
#         """
#         Threaded callback function to receive audio data when recordings finish.
#         audio: An AudioData containing the recorded bytes.
#         """
#         # Grab the raw bytes and push it into the thread safe queue.
#         # data = audio.get_raw_data()
#         # data_queue.put(data)
#         print("asas")
#         print(recognizer.recognize(audio))
#     # Create a background thread that will pass us raw audio bytes.
#     # We could do this manually but SpeechRecognizer provides a nice helper.
#     recorder.listen_in_background(source, record_callback)

#     # Cue the user that we're ready to go.
#     print("Model loaded.\n")
#     while True:
#         sleep(0.1)
    

# main()

# import pyaudio
# import wave

# chunk = 1024  # Record in chunks of 1024 samples
# sample_format = pyaudio.paInt16  # 16 bits per sample
# channels = 2
# fs = 44100  # Record at 44100 samples per second
# seconds = 3
# filename = "output.wav"

# p = pyaudio.PyAudio()  # Create an interface to PortAudio

# print('Recording')

# stream = p.open(format=sample_format,
#                 channels=channels,
#                 rate=fs,
#                 frames_per_buffer=chunk,
#                 input=True)

# frames = []  # Initialize array to store frames

# # Store data in chunks for 3 seconds
# for i in range(0, int(fs / chunk * seconds)):
#     data = stream.read(chunk)
#     frames.append(data)

# # Stop and close the stream 
# stream.stop_stream()
# stream.close()
# # Terminate the PortAudio interface
# p.terminate()

# print('Finished recording')

# # Save the recorded data as a WAV file
# wf = wave.open(filename, 'wb')
# wf.setnchannels(channels)
# wf.setsampwidth(p.get_sample_size(sample_format))
# wf.setframerate(fs)
# wf.writeframes(b''.join(frames))
# wf.close()

# import pyaudio

# p = pyaudio.PyAudio()
# info = p.get_host_api_info_by_index(0)
# numdevices = info.get('deviceCount')

# for i in range(0, numdevices):
#     if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
#         print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

import speech_recognition as sr
from time import sleep
import traceback

recognizer = sr.Recognizer()
mic = sr.Microphone()

try:
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("start listenning")
        audio = recognizer.record(mic, duration=5)
        print("stop listenning")

        print(recognizer.recognize(audio)) #Output
except Exception:
    print(traceback.format_exc())


# while True: 
#     sleep(0.1)