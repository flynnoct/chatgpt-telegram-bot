FROM python:3.9-alpine

# Install dependencies
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Copy the rest of the code
COPY . .

RUN cp config.json.template config.json \
    && sed -i 's/<YOUR_OPENAI_API_KEY_HERE>/$OPENAI_API_KEY/g' config.json \
    && sed -i 's/<YOUR_TELEGRAM_BOT_TOKEN_HERE>/$TELEGRAM_BOT_TOKEN/g' config.json \

CMD ["sh", "docker_start.sh"]

