from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import CommandError

User = get_user_model()


class Command(createsuperuser.Command):
    help = 'Create a superuser for Westforce (single-user system)'

    def handle(self, *args, **options):
        if User.objects.exists():
            raise CommandError('A manager user already exists. Use create_manager command instead.')
        
        try:
            return super().handle(*args, **options)
        except ValidationError as e:
            raise CommandError(str(e))
