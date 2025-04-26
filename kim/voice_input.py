import speech_recognition as sr

def recognize_speech_from_microphone():
    """
    Captures audio from the microphone and converts it into text.
    This function returns the recognized text or None if no speech is recognized.
    """
    recognizer = sr.Recognizer()  # Initialize the recognizer for speech recognition.
    
    # Use the microphone as the audio source
    with sr.Microphone() as source:
        print("Listening... Please say something.")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise levels.
        audio = recognizer.listen(source)  # Capture the speech.

    try:
        # Use Google Web Speech API to transcribe speech into text
        print("Recognizing speech...")
        text = recognizer.recognize_google(audio)  # This sends the audio to Google's servers for recognition.
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        # This error is raised when the speech is not recognized
        print("Sorry, I could not understand your speech.")
        return None
    except sr.RequestError:
        # This error is raised when there's a problem with the API service
        print("There was an issue with the speech recognition service. Please check your internet connection.")
        return None
