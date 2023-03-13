import azure.cognitiveservices.speech as speechsdk


class AzureSpeech:
    def __init__(self, speechKey, speechRegion):
        self.speechKey = speechKey
        self.speechRegion = speechRegion
        self.speech_config = speechsdk.SpeechConfig(subscription=self.speechKey, region=self.speechRegion)
        self.speech_config.speech_recognition_language = "en-US"
        self.speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config,
                                                            audio_config=self.audio_config)
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config,
                                                              audio_config=self.audio_config)

    def recognize_from_microphone(self):
        print("Say something...")
        speech_recognition_result = self.speech_recognizer.recognize_once_async().get()
        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {"success": True, "message": speech_recognition_result.text}
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            return {"success": False,
                    "message": "No speech could be recognized: {}".format(speech_recognition_result.no_match_details)}
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            return {"success": False, "message": "Speech Recognition canceled: {}".format(cancellation_details.reason)}

    def text_to_speech(self, text):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return {"success": True, "message": "Speech synthesized to speaker for text [{}]".format(text)}
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            return {"success": False, "message": "Speech synthesis canceled: {}".format(cancellation_details.reason)}
