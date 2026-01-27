import datetime

from django.conf import settings
from django.db import models
# Django 3.2: JSONField pot ser aquí
from django.db.models import JSONField
from django.urls import reverse
from django.utils import timezone


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("gaming", "Gaming"),
        ("music", "Música"),
        ("talk", "Xerrades"),
        ("education", "Educació"),
        ("sports", "Esports"),
        ("entertainment", "Entreteniment"),
        ("technology", "Tecnologia"),
        ("art", "Art i Creativitat"),
        ("other", "Altres"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Programat"),
        ("live", "En Directe"),
        ("finished", "Finalitzat"),
        ("cancelled", "Cancel·lat"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    scheduled_date = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    thumbnail = models.ImageField(upload_to="events/thumbnails/", blank=True, null=True)
    max_viewers = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True)
    stream_url = models.URLField(max_length=500, blank=True)

    # Emmagatzema el vector numèric (embedding) com una llista de floats
    embedding = models.JSONField(blank=True, null=True)

    # Nom del model d'IA utilitzat (per si canviem de model en el futur)
    embedding_model = models.CharField(max_length=200, blank=True, null=True)

    # Data de l'última actualització de l'embedding
    embedding_updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Esdeveniment"
        verbose_name_plural = "Esdeveniments"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("events:event_detail", kwargs={"pk": self.pk})

    @property
    def is_live(self):
        return self.status == "live"

    @property
    def is_upcoming(self):
        return self.status == "scheduled" and self.scheduled_date > timezone.now()

    def get_duration(self):
        category_durations = {
            "gaming": 180,  # 3 hores
            "music": 90,  # 1.5 hores
            "talk": 60,  # 1 hora
            "education": 120,  # 2 hores
            "sports": 150,  # 2.5 hores
            "entertainment": 120,  # 2 hores
            "technology": 90,  # 1.5 hores
            "art": 120,  # 2 hores
            "other": 90,  # 1.5 hores
        }
        minutes = category_durations.get(self.category, 90)
        return datetime.timedelta(minutes=minutes)

    def get_tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]


def get_stream_embed_url(self):
    if not self.stream_url:
        return None

    url = self.stream_url
    if "youtube.com/watch" in url:
        video_id = url.split("v=")[1].split("&")[0]
        return f"https://www.youtube-nocookie.com/embed/{video_id}"
    elif "youtu.be/" in url:
        video_id = url.split("/")[-1]
        return f"https://www.youtube-nocookie.com/embed/{video_id}"
    elif "twitch.tv/" in url:
        channel = url.split("/")[-1]
        return f"https://player.twitch.tv/?channel={channel}&parent=localhost&parent=127.0.0.1"
    return url
