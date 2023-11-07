import os
import langid
import azure.cognitiveservices.speech as speechsdk
from config_loader import ConfigLoader
from logging_manager import LoggingManager

class AzureParser:

    # return true for success, false for failure
    def text_to_speech(self, text, file_id):
        LoggingManager.info("Get Azure TTS request, file save to %s" % file_id, "AzureParser")
        speech_config = speechsdk.SpeechConfig(subscription=ConfigLoader.get("azure_tts", "subscription_key"), region=ConfigLoader.get("azure_tts", "subscription_region"))
        # https://learn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts
        language, voice = self._detect_language(text)
        speech_config.speech_synthesis_language = language # will be ignored if voice is specified
        speech_config.speech_synthesis_voice_name = voice
        audio_config = speechsdk.audio.AudioOutputConfig(filename="%s.wav" % file_id) # TODO: stream?
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        # check result, thank you microsoft for your shitty documentation :)
        if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            LoggingManager.error("Speech synthesis canceled: %s" % str(cancellation_details.reason), "AzureParser")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    LoggingManager.error("Error details: %s" % cancellation_details.error_details, "AzureParser")


    def _detect_language(self, text):
        # https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts
        voice = ConfigLoader.get("azure_tts", "voice")
        language = ConfigLoader.get("azure_tts", "language")
        if voice != "": # voice is specified
            try:
                language = voice.split("-")[0] + "-" + voice.split("-")[1].upper()
                return (language, voice)
            except:
                LoggingManager.critical("Azure voice name is not valid: %s, check https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support?tabs=tts" % voice, "AzureParser")
                return ("en-US", "")
        elif language != "": # language is specified
            return (language, "")
        else: # detect language
            language = langid.classify(text)[0]
            print(language)
            supported_languages = {'af': 'af-ZA', 'am': 'am-ET', 'ar': 'ar-SA', 'bg': 'bg-BG', 'bn': 'bn-BD', 'bs': 'bs-BA', 'ca': 'ca-ES', 'cs': 'cs-CZ', 'cy': 'cy-GB', 'da': 'da-DK', 'de': 'de-DE', 'el': 'el-GR', 'en': 'en-US', 'es': 'es-ES', 'et': 'et-EE', 'eu': 'eu-ES', 'fa': 'fa-IR', 'fi': 'fi-FI', 'fil': 'fil-PH', 'fr': 'fr-FR', 'ga': 'ga-IE', 'gl': 'gl-ES', 'gu': 'gu-IN', 'he': 'he-IL', 'hi': 'hi-IN', 'hr': 'hr-HR', 'hu': 'hu-HU', 'hy': 'hy-AM', 'id': 'id-ID', 'is': 'is-IS', 'it': 'it-IT', 'ja': 'ja-JP', 'jv': 'jv-ID', 'ka': 'ka-GE', 'kk': 'kk-KZ', 'km': 'km-KH', 'kn': 'kn-IN', 'ko': 'ko-KR', 'lo': 'lo-LA', 'lt': 'lt-LT', 'lv': 'lv-LV', 'mk': 'mk-MK', 'ml': 'ml-IN', 'mn': 'mn-MN', 'mr': 'mr-IN', 'ms': 'ms-MY', 'my': 'my-MM', 'nb': 'nb-NO', 'ne': 'ne-NP', 'nl': 'nl-NL', 'pl': 'pl-PL', 'ps': 'ps-AF', 'pt': 'pt-PT', 'ro': 'ro-RO', 'ru': 'ru-RU', 'si': 'si-LK', 'sk': 'sk-SK', 'sl': 'sl-SI', 'so': 'so-SO', 'sq': 'sq-AL', 'sr': 'sr-RS', 'su': 'su-ID', 'sv': 'sv-SE', 'sw': 'sw-KE', 'ta': 'ta-IN', 'te': 'te-IN', 'th': 'th-TH', 'tr': 'tr-TR', 'uk': 'uk-UA', 'ur': 'ur-PK', 'uz': 'uz-UZ', 'vi': 'vi-VN', 'wuu': 'wuu-CN', 'yue': 'yue-HK', 'zh': 'zh-CN', 'zu': 'zu-ZA'}
            if language not in supported_languages:
                LoggingManager.error("Language %s is not supported by Azure TTS" % language, "AzureParser")
                return ("en-US", "")
            else:
                return (supported_languages[language], "")

        
