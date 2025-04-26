import speech_recognition as sr
from kim.brain import process_message, generate_question, handle_calendar_commands
from kim.calendar_api import authenticate_google_calendar

# Autentica no Google Calendar
calendar_service = authenticate_google_calendar()

# Inicializa variáveis
user_profile = ""  # Corrigido: o profile é uma string que vai ser atualizada
conversation_history = ""

def main():
    global user_profile  # Certifica que estamos utilizando a variável global para garantir que a atualização aconteça corretamente.
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Kim is listening... Say something!")

    while True:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening... Please say something.")
            audio = recognizer.listen(source)

        try:
            message = recognizer.recognize_google(audio)
            print(f"You said: {message}")

            # Primeiro tenta ver se é um comando de calendário
            calendar_response = handle_calendar_commands(message, calendar_service)
            if calendar_response:
                print(f"Kim (calendar): {calendar_response}")
                continue

            # Se não for de calendário, trata como mensagem normal
            updated_profile = process_message(message, user_profile)
            print(f"Kim (profile updated): {updated_profile}")

            # Atualiza o profile global
            user_profile = updated_profile

            conversation_history += f"\nUser: {message}"

            # Gera uma nova pergunta para continuar a conversa
            next_question = generate_question(user_profile, conversation_history)
            print(f"Kim: {next_question}")

        except sr.UnknownValueError:
            print("Sorry, I did not understand. Could you repeat?")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    main()
