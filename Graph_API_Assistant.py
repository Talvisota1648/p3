import requests
import json
import argparse
from datetime import datetime

# Конфигурация
API_URL = "https://api.nikta.ai/api/v1/run_workflow_as_server"
WORKFLOW_ID = "13"  # Замените на ваш ID воркфлоу
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NzkwMTQ5MywianRpIjoiNmZmYmQyNGUtYjE4Mi00MzM1LTliYTktNjM2NTE1YjIzMWY4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3Njc5MDE0OTMsImNzcmYiOiI0NzY3MDk4Mi03OGMwLTQ5NDUtODlhMy03YWI0OGYxM2MxYzkiLCJleHAiOjE3Njc5ODc4OTN9.8PS2m7SZ0zdI9OvUw6e2DPlvi54EvTs00-yCMRJajhs"  # Замените на ваш токен
BOT_TOKEN = "8285176607:AAGd6CfMnbAdUUIo-zZMQ3542q2f-ByTlEE"  # Токен бота @RoadMap_Anomaly_bot
CHAT_ID = "5107472744"  # ID чата с ботом


class NiktaGraphClient:
    def __init__(self, workflow_id, access_token):
        self.workflow_id = workflow_id
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def send_request(self, prompt):
        payload = {
            "workflow_id": self.workflow_id,
            "prompt": prompt,
            "stream": False
        }

        response = self.session.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()["result"]


def save_to_history(prompt, response):
    with open("history.json", "a") as f:
        record = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="AI Assistant for Project Manager")
    parser.add_argument("prompt", help="Task description in natural language")
    args = parser.parse_args()

    # Отправка запроса в Nikta Graph
    client = NiktaGraphClient(WORKFLOW_ID, ACCESS_TOKEN)
    try:
        response = client.send_request(args.prompt)
        print("\n🤖 AI Response:")
        print(response)

        # Сохранение истории
        save_to_history(args.prompt, response)

        # Отправка сообщения в Telegram
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        message_data = {
            "chat_id": CHAT_ID,
            "text": f"📝 Task: {args.prompt}\n\n🎯 AI Response:\n{response}"
        }
        requests.post(telegram_url, json=message_data)

    except requests.exceptions.HTTPError as e:
        print(f"API request failed: {e.response.status_code} {e.response.reason}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()