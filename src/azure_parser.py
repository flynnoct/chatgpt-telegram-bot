import os
import azure.cognitiveservices.speech as speechsdk
from config_loader import ConfigLoader
from logging_manager import LoggingManager

class AzureParser:

    def text_to_speech(self, text, file_id):
        LoggingManager.info("Get Azure TTS request, file save to %s" % file_id, "AzureParser")
        speech_config = speechsdk.SpeechConfig(subscription=ConfigLoader.get("azure_tts")["subscription_key"], region=ConfigLoader.get("azure_tts")["subscription_region"])
        # https://learn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts
        speech_config.speech_synthesis_language = "zh-CN" # will be ignored if voice is specified
        speech_config.speech_synthesis_voice_name ="zh-CN-XiaoxiaoNeural"
        audio_config = speechsdk.audio.AudioOutputConfig(filename="%s.wav" % file_id) # TODO: stream?
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
