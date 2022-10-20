import pvporcupine
import pvrhino
import argparse
import os
import struct
import sys
from threading import Thread

import numpy as np
import pyaudio
import soundfile
import pyttsx3
import time

from halo import Halo

class OrderProcessor:
    
    def __init__(self, args):
        self.wakeword_engine = pvporcupine.create(keywords=['picovoice'])
        self.wakeword_engine_frame_length = self.wakeword_engine.frame_length

        self.nlu_engine = pvrhino.create(library_path=pvrhino.LIBRARY_PATH, 
                                        model_path=pvrhino.MODEL_PATH,
                                        context_path=args.context_path)
        self.nlu_engine_frame_length = self.nlu_engine.frame_length  

        self.spinner = Halo(text='Listening', spinner='dots')

        self.start_audio_input()
        self.engine = pyttsx3.init()
        self.menu_prices = {"hamburger":1.99,
                            "wrap":1.3,
                            "chicken burger": 1.1,
                            "fish burger": 1.5,
                            "french fries": 0.5,
                            "salad": 0.6,
                            "corn": 0.4,
                            "coke": 0.2,
                            "sprite": 0.2,
                            "diet coke": 0.2,
                            "orange juice": 0.2}

    def start_audio_input(self):

        self.pa = pyaudio.PyAudio()

        self.audio_stream = self.pa.open(
            rate=self.wakeword_engine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.wakeword_engine.frame_length)

    def stop_audio_input(self):

        if self.audio_stream is not None:
            self.audio_stream.close()

        if self.pa is not None:
            self.pa.terminate()

    def get_frame(self, frame_length):
        self.spinner.start()
        pcm = self.audio_stream.read(frame_length, exception_on_overflow = False)
        pcm = struct.unpack_from("h" * frame_length, pcm)
        return pcm

    def play_sound(self):
        pass

    def speak(self, phrase):
        self.spinner.stop()
        self.stop_audio_input()
        print(phrase)
        self.engine.say(phrase)
        self.engine.runAndWait()
        self.engine.stop()
        self.start_audio_input()

    def wait_for_keyword(self):
        while True:
            keyword_index = self.wakeword_engine.process(self.get_frame(self.wakeword_engine_frame_length))
            if keyword_index >= 0:
                return True

    def process_order(self):

        order = []             
        while True:

            is_finalized = self.nlu_engine.process(self.get_frame(self.nlu_engine_frame_length))

            if is_finalized:
                inference = self.nlu_engine.get_inference()

                if inference.is_understood and inference.intent == 'orderFood':
                    order = [value for slot, value in inference.slots.items()]
                    print(order)
                    phrase = 'Your order is {}. Is this correct?'.format(" and ".join(order))
                    return order, phrase
                else:
                    phrase = "\nDidn't understand your order. Can you repeat?"
                    print(phrase)


    def wait_for_confirmation(self):
        while True:

            is_finalized = self.nlu_engine.process(self.get_frame(self.nlu_engine_frame_length))

            if is_finalized:
                inference = self.nlu_engine.get_inference()

                if inference.is_understood:
                    if inference.intent == 'confirm':
                        return True
                    if inference.intent == 'cancel':
                        return False                       
                else:
                    phrase = "\nDidn't understand what you said. Can you repeat?"
                    print(phrase)

    def finish_order(self):
        pass

    def main(self):
        while True:
            try:
                    self.wait_for_keyword()
                    self.speak('Welcome to order at Robo Fast Food.')
                    time.sleep(0.5)
                    self.order, phrase = self.process_order()
                    self.speak(phrase)
                    time.sleep(0.5)
                    result = self.wait_for_confirmation()
                    if result:
                        total = sum([self.menu_prices[item] for item in self.order])
                        phrase = "Your order total is {} USD. Please scan the QR code to pay. Enjoy your meal!".format(total)
                    else:
                        phrase = "Alright. Welcome to come back again!"
                    self.speak(phrase)

            except KeyboardInterrupt:
                self.stop_audio_input()
                self.wakeword_engine.delete()

parser = argparse.ArgumentParser()
parser.add_argument('--context_path', help="Absolute path to context file.")
args = parser.parse_args()

processor = OrderProcessor(args)
processor.main()