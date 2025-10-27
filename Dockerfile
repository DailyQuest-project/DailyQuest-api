# Usar a imagem oficial do Python
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copia AMBOS os arquivos de dependência
COPY requirements.txt requirements-dev.txt ./

# Instala as dependências PRINCIPAIS
RUN pip install --no-cache-dir -r requirements.txt

# Instala as dependências de DESENVOLVIMENTO (linters, testes)
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copiar a pasta 'src' inteira para dentro do container, na pasta de trabalho
COPY ./src /app/src

# Comando para iniciar a aplicação. O Uvicorn vai encontrar 'src.main' corretamente.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]