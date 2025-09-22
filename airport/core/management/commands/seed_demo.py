from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Airport, AirplaneType, Airplane, Route, Crew, Flight

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo data for Airport API"

    def handle(self, *args, **opts):
        self.stdout.write("Seeding demo data...")
        admin, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
        admin.set_password("adminpass"); admin.save()
        user, _ = User.objects.get_or_create(username="user")
        user.set_password("userpass"); user.save()

        kyiv, _ = Airport.objects.get_or_create(name="Kyiv ZH", closest_big_city="Kyiv")
        paris, _ = Airport.objects.get_or_create(name="Paris CDG", closest_big_city="Paris")
        a320, _ = AirplaneType.objects.get_or_create(name="A320")
        plane, _ = Airplane.objects.get_or_create(name="UR-AAA", rows=10, seats_in_row=6, airplane_type=a320)
        route, _ = Route.objects.get_or_create(source=kyiv, destination=paris, distance=2400)
        crew1, _ = Crew.objects.get_or_create(first_name="John", last_name="Doe")

        now = datetime.utcnow()
        fl, _ = Flight.objects.get_or_create(
            route=route,
            airplane=plane,
            departure_time=now + timedelta(days=1),
            arrival_time=now + timedelta(days=1, hours=3),
        )
        fl.crew.add(crew1)
        self.stdout.write(self.style.SUCCESS("Demo data: admin/adminpass, user/userpass"))
