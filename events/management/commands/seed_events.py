import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event


class Command(BaseCommand):
    help = "Seeds the database with initial event data"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Create a test user if none exists
        if not User.objects.exists():
            self.stdout.write("Creating default user...")
            user = User.objects.create_user("admin", "admin@example.com", "password123")
            user.is_superuser = True
            user.is_staff = True
            user.save()

        users = list(User.objects.all())

        categories = [
            "gaming",
            "music",
            "talk",
            "education",
            "sports",
            "entertainment",
            "technology",
            "art",
            "other",
        ]
        statuses = ["scheduled", "live", "finished", "cancelled"]

        # Events data
        events_data = [
            {
                "title": "Torneig LOL Final",
                "category": "gaming",
                "stream_url": "https://www.twitch.tv/lolesports",
            },
            {
                "title": "Curs Python Avançat",
                "category": "education",
                "stream_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
            },
            {
                "title": "Concert en Viu: Jazz Night",
                "category": "music",
                "stream_url": "https://www.youtube.com/watch?v=neV3EPgvZ3g",
            },
            {
                "title": "Tech Talk: AI Future",
                "category": "technology",
                "stream_url": "https://www.youtube.com/watch?v=2i884g89h_g",
            },
            {
                "title": "Final Champions League",
                "category": "sports",
                "stream_url": "https://www.twitch.tv/kingsleague",
            },
            {
                "title": "Taller de Pintura a l'Oli",
                "category": "art",
                "stream_url": "https://www.youtube.com/watch?v=7M0U_V2gY10",
            },
            {
                "title": "Podcast: Vida Digital",
                "category": "talk",
                "stream_url": "https://www.youtube.com/watch?v=D-279L181e8",
            },
            {
                "title": "Speedrun Mario 64",
                "category": "gaming",
                "stream_url": "https://www.twitch.tv/gamesdonequick",
            },
            {
                "title": "Curs de Cuina Vegana",
                "category": "other",
                "stream_url": "https://www.youtube.com/watch?v=Vz2y3Bw_bEw",
            },
            {
                "title": "Presentació Nou iPhone",
                "category": "technology",
                "stream_url": "https://www.youtube.com/watch?v=K4TOrB7at0Y",
            },
            {
                "title": "Gala dels Oscars",
                "category": "entertainment",
                "stream_url": "https://www.youtube.com/watch?v=Uq76c7s7bMI",
            },
            {
                "title": "Classe de Ioga",
                "category": "sports",
                "stream_url": "https://www.youtube.com/watch?v=v7SN-d4qXx0",
            },
            {
                "title": "Tutorial React JS",
                "category": "education",
                "stream_url": "https://www.youtube.com/watch?v=w7ejDZ8SWv8",
            },
            {
                "title": "Stand-up Comedy Special",
                "category": "entertainment",
                "stream_url": "https://www.netflix.com",
            },
            {
                "title": "Exposició Art Modern",
                "category": "art",
                "stream_url": "https://www.youtube.com/watch?v=0p_W_5j1c8o",
            },
        ]

        self.stdout.write("Seeding events...")

        for i, data in enumerate(events_data):
            # Random status but make sure we have some of each
            if i < 3:
                status = "live"
            elif i < 8:
                status = "scheduled"
            elif i < 13:
                status = "finished"
            else:
                status = "cancelled"

            # Date based on status
            if status == "live":
                date = timezone.now()
            elif status == "scheduled":
                date = timezone.now() + timedelta(days=random.randint(1, 10))
            else:
                date = timezone.now() - timedelta(days=random.randint(1, 10))

            Event.objects.create(
                title=data["title"],
                description=f"Descripció detallada per {data['title']}. Aquest és un esdeveniment de prova creat automàticament.",
                creator=random.choice(users),
                category=data["category"],
                scheduled_date=date,
                status=status,
                max_viewers=random.randint(50, 5000),
                is_featured=random.choice([True, False])
                if status != "cancelled"
                else False,
                tags=f"{data['category']}, streaming, {status}",
                stream_url=data["stream_url"],
            )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(events_data)} events")
        )
