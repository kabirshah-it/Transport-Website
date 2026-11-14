
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the administrator account for the Render test website."

    def handle(self, *args, **options):
        username = os.environ.get("RENDER_ADMIN_USERNAME")
        password = os.environ.get("RENDER_ADMIN_PASSWORD")
        email = os.environ.get("RENDER_ADMIN_EMAIL", "")

        if not username or not password:
            raise CommandError(
                "Set RENDER_ADMIN_USERNAME and RENDER_ADMIN_PASSWORD."
            )

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING("Render admin account already exists.")
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS("Render admin account created successfully.")
        )
