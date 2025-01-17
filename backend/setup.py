import os
import django
from django.core.management import call_command


def setup():
    print("Setting up the database...")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    try:
        print("Running migrations...")
        call_command("migrate")
        print("\nSetup completed successfully!")
        print("\nYou can now run the server with:")
        print("python manage.py runserver")
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        print("Please make sure you have the correct database settings in .env")


if __name__ == "__main__":
    setup()
