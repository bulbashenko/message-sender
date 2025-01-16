import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


def test_whatsapp_message():
    """
    Test WhatsApp message sending using Meta Cloud API
    """
    # Get configuration from environment
    api_url = os.getenv("WHATSAPP_API_URL")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    test_number = os.getenv("WHATSAPP_TEST_NUMBER")

    if not all([api_url, phone_number_id, access_token, test_number]):
        print("Error: Missing WhatsApp configuration. Please check your .env file.")
        return False

    # Prepare the API request
    url = f"{api_url}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": test_number,
        "type": "text",
        "text": {"body": "Hello! This is a test message from your Django app."},
    }

    try:
        # Send the message
        response = requests.post(url, headers=headers, json=data)
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
    test_whatsapp_message()
