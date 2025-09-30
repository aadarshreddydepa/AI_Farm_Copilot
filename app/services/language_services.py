import os
import speech_recognition as sr
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator


# To ensure consistent language detection
DetectorFactory.seed = 0


class LanguageProcessor:
    """
    Handles:
    1. Detecting language of input text/audio
    2. Translating input to English
    3. Translating AI answers back to user's language
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def process_input(self, input_data: str, is_audio: bool = False):
        """
        Process input from text or audio.
        Returns (processed_text_in_english, detected_language_code)
        """
        if not input_data:
            raise ValueError("Input text/audio path is empty")

        if is_audio:
            return self._process_audio(input_data)
        else:
            return self._process_text(input_data)

    def _process_text(self, text: str):
        """
        Detect language and translate text to English.
        """
        detected_lang = self._detect_language(text)

        # If already English, no need to translate
        if detected_lang == "en":
            return text, detected_lang

        translated = GoogleTranslator(source=detected_lang, target="en").translate(text)
        return translated, detected_lang

    def _process_audio(self, audio_file: str):
        """
        Convert speech to text, detect language, translate to English.
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)

        try:
            recognized_text = self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            raise ValueError("Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            raise ConnectionError(f"Speech Recognition API error: {e}")

        return self._process_text(recognized_text)

    def _detect_language(self, text: str) -> str:
        """
        Detect the language of a text string.
        """
        try:
            if len(text.strip()) < 3:
                return "en"  # too short → default to English
            return detect(text)
        except Exception:
            return "en"

    def translate_to_language(self, text: str, target_lang: str, source_lang: str = "en"):
        """
        Translate text into any target language.
        """
        if not text:
            raise ValueError("No text provided for translation")

        try:
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
            return translated
        except Exception:
            return text  # fallback: return original text if translation fails


# ------------------- TESTING -------------------
if __name__ == "__main__":
    processor = LanguageProcessor()

    print("📝 Testing with French text...")
    text_input = "Bonjour, comment puis-je planter des tomates?"
    processed_text, user_lang = processor.process_input(text_input)
    print("Processed (English):", processed_text)
    print("Original Language:", user_lang)

    back_translation = processor.translate_to_language(processed_text, user_lang)
    print("Back translation:", back_translation)
    print("-" * 60)

    print("📝 Testing with English short text...")
    short_input = "Hi"
    processed_text, user_lang = processor.process_input(short_input)
    print("Processed (English):", processed_text)
    print("Original Language:", user_lang)
    print("-" * 60)

    print("📝 Testing with Empty input...")
    try:
        processor.process_input("")
    except Exception as e:
        print("Expected error:", e)
    print("-" * 60)

    # 👇 Uncomment once you have a test_es.wav file recorded
    # print("🎤 Testing with Spanish audio...")
    # processed_text, user_lang = processor.process_input("test_es.wav", is_audio=True)
    # print("Processed (English):", processed_text)
    # print("Original Language:", user_lang)
    # print("-" * 60)

    print("🔄 Testing translation back to Telugu...")
    english_answer = "How everyone is cultivating the Cabagge?"
    translated_answer = processor.translate_to_language(english_answer, "te")
    print("Answer in Telugu:", translated_answer)