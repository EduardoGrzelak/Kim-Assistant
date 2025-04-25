from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a chave da OpenAI
openai_key = os.getenv("OPENAI_API_KEY")

# Verificar se a chave foi carregada corretamente
if openai_key:
    print("✅ OpenAI key loaded successfully!")
    print(f"Chave carregada: {openai_key}")  # Isso vai mostrar a chave (não compartilhe isso publicamente)
else:
    print("❌ Failed to load OpenAI key.")
