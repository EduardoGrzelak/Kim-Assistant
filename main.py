from kim.voice_input import recognize_speech_from_microphone

def main():
    # Test the voice input function
    user_message = recognize_speech_from_microphone()
    if user_message:
        print(f"User said: {user_message}")
    else:
        print("No speech recognized.")
    
if __name__ == "__main__":
    main()
