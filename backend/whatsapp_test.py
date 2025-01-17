import os
from dotenv import load_dotenv
import requests

load_dotenv()


def test_whatsapp_message(message_text=None):
    api_url = os.getenv("WHATSAPP_API_URL")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    test_number = os.getenv("WHATSAPP_TEST_NUMBER")

    if not all([api_url, phone_number_id, access_token, test_number]):
        print("Error: Missing WhatsApp configuration. Please check your .env file.")
        return False

    url = f"{api_url}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": test_number,  # Format: +XXXXXXXXXXXX 
        "type": "text",
        "text": {
            "preview_url": True,
            "body": message_text
            or "Hello! This is a custom message from your Django app.",
        },
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(url, headers, data)
        response_data = response.json()

        if response.status_code in [200, 201]:
            print("Success! WhatsApp message sent.")
            print(f"Message ID: {response_data['messages'][0]['id']}")
            return True
        else:
            print(f"Error: Failed to send WhatsApp message.")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing WhatsApp Integration...")
    custom_message = input(
        "Enter your message (press Enter for default message): "
    ).strip()
    test_whatsapp_message(custom_message if custom_message else None)
