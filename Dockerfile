# Usar a imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho no contêiner
WORKDIR /app

# Copiar o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do aplicativo para o contêiner
COPY . .

# Expor a porta que o Flask usa
EXPOSE 59998

# Definir a variável de ambiente para executar o Flask
ENV FLASK_APP=app.py

# Comando para executar o aplicativo
CMD ["flask", "run", "--host=0.0.0.0", "--port=59998"]
