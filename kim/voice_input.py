import speech_recognition as sr
import time

def recognize_speech_from_microphone():
    """
    Captures audio from the microphone and converts it into text.
    Returns the recognized text or None if no speech is recognized.
    """
    recognizer = sr.Recognizer()
    
    # Adjusted listening parameters
    recognizer.pause_threshold = 1.5    # Longer pause before considering speech ended
    recognizer.energy_threshold = 4000  # Sensitivity adjustment
    recognizer.dynamic_energy_threshold = True  # Auto-adjust for noisy environments

    with sr.Microphone() as source:
        print("Listening... Please speak now.")
        
        # Adjust for ambient noise with longer duration
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        
        try:
            # Timeout settings:
            # - 5 seconds to start speaking
            # - 10 seconds maximum phrase length
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Small processing delay
            time.sleep(0.3)
            
            print("Processing your speech...")
            
            # Using Google Web Speech API with explicit English language
            text = recognizer.recognize_google(audio, language='en-US')
            print(f"You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("I didn't hear anything. Please try again.")
            return None
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand your speech.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {str(e)}")
            return None