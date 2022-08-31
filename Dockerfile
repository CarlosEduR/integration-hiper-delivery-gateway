FROM sanicframework/sanic:3.8-latest

WORKDIR /app

COPY . /app

ENV TZ=America/Sao_Paulo

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["sanic", "main.application", "--host=0.0.0.0", "--port=8000", "--workers=10"]