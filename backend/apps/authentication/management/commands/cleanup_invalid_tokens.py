from django.core.management.base import BaseCommand
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Cleans up invalid token records that reference non-existent users'

    def handle(self, *args, **options):
        # Get all tokens
        tokens = OutstandingToken.objects.all()
        cleaned = 0

        for token in tokens:
            # Check if the user exists
            if not User.objects.filter(id=token.user_id).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Removing token {token.id} with invalid user_id {token.user_id}'
                    )
                )
                token.delete()
                cleaned += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {cleaned} invalid token records'
            )
        )