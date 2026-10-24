import os

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crée les comptes de démonstration analyste, lecteur et admin (développement uniquement)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_users est réservé au développement")
        pwd = os.environ.get("DEMO_PASSWORD", "demo-pass-change-me")
        grp, _ = Group.objects.get_or_create(name="analyste")
        for name, staff in (("analyste", False), ("lecteur", False), ("admin", True)):
            u, _ = User.objects.get_or_create(
                username=name, defaults={"is_staff": staff, "is_superuser": staff}
            )
            u.set_password(pwd)
            u.save()
        User.objects.get(username="analyste").groups.add(grp)
        self.stdout.write("Comptes créés : analyste (peut expliquer), lecteur (lecture seule), admin")