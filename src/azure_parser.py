import os
import azure.cognitiveservices.speech as speechsdk
from config_loader import ConfigLoader

class AzureParser:

    def text_to_speech(self, text, file_id):
        speech_config = speechsdk.SpeechConfig(subscription=ConfigLoader.get("azure_tts")["subscription_key"], region=ConfigLoader.get("azure_tts")["subscription_region"])
        # https://learn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts
        speech_config.speech_synthesis_language = "zh-CN" # will be ignored if voice is specified
        speech_config.speech_synthesis_voice_name ="zh-CN-XiaoxiaoNeural"
        audio_config = speechsdk.audio.AudioOutputConfig(filename="%s.wav" % file_id) # TODO: format?
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

# if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#     print("Speech synthesized for text [{}]".format(text))
# elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
#     cancellation_details = speech_synthesis_result.cancellation_details
#     print("Speech synthesis canceled: {}".format(cancellation_details.reason))
#     if cancellation_details.reason == speechsdk.CancellationReason.Error:
#         if cancellation_details.error_details:
#             print("Error details: {}".format(cancellation_details.error_details))
#             print("Did you set the speech resource key and region values?")