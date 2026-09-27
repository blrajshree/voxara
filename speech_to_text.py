import speech_recognition as sr
from deep_translator import GoogleTranslator


# -------------------------------------------------
# LANGUAGE SETTINGS
# -------------------------------------------------

LANGUAGES = {
    "English": "en-IN",
    "Tamil": "ta-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN"
}


# -------------------------------------------------
# SPEECH TO TEXT
# -------------------------------------------------

def speech_to_text(language_code="en-IN"):

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""


    try:

        text = recognizer.recognize_google(
            audio,
            language=language_code
        )

        print("Recognized:", text)

        return text

    except sr.UnknownValueError:

        print("Could not understand speech.")
        return ""

    except sr.RequestError as e:

        print("Speech recognition error:", e)
        return ""


# -------------------------------------------------
# TRANSLATION
# -------------------------------------------------

def translate_text(text, target_language):

    if not text:
        return ""

    # If target is English
    if target_language == "en":
        return text

    try:

        translated = GoogleTranslator(
            source="auto",
            target=target_language
        ).translate(text)

        return translated

    except Exception as e:

        print("Translation error:", e)

        return text


# -------------------------------------------------
# COMPLETE SPEECH → TRANSLATION FUNCTION
# -------------------------------------------------

def speech_to_translated_text(
        speech_language="en-IN",
        target_language="ta"):

    # Step 1: Speech → Text
    text = speech_to_text(speech_language)

    if not text:
        return ""

    # Step 2: Text → Selected language
    translated_text = translate_text(
        text,
        target_language
    )

    print("--------------------------------")
    print("Original :", text)
    print("Translated:", translated_text)
    print("--------------------------------")

    return translated_text


# -------------------------------------------------
# TEST
# -------------------------------------------------

if __name__ == "__main__":

    print("VOXARA Speech Translation Test")

    # Hearing person's speaking language
    source_language = "en-IN"

    # Deaf person's selected language
    target_language = "ta"

    result = speech_to_translated_text(
        source_language,
        target_language
    )

    print("Final output:", result)