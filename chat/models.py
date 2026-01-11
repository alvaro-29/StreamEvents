# Model per al sistema de xat en temps real
from django.conf import settings
from django.db import models
from django.utils.timesince import timesince

from events.models import Event


class ChatMessage(models.Model):
    """
    Model que representa un missatge de xat en un esdeveniment.
    Permet soft delete i destacar missatges pel creador de l'event.
    """

    # Relacions
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Esdeveniment",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Usuari",
    )

    # Camps de contingut
    message = models.TextField(max_length=500, verbose_name="Missatge")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creat")

    # Camps d'estat
    is_deleted = models.BooleanField(default=False, verbose_name="Eliminat")
    is_highlighted = models.BooleanField(default=False, verbose_name="Destacat")

    class Meta:
        ordering = ["created_at"]  # Més antic primer
        verbose_name = "Missatge de Xat"
        verbose_name_plural = "Missatges de Xat"

    def __str__(self):
        """Retorna: 'username: primeres 50 lletres del missatge'"""
        return f"{self.user.username}: {self.message[:50]}"

    def can_delete(self, user):
        """
        Retorna True si l'usuari pot eliminar aquest missatge.
        Pot eliminar: el creador del missatge, el creador de l'esdeveniment, o staff.
        """
        if not user.is_authenticated:
            return False
        return (
            self.user == user  # Creador del missatge
            or self.event.creator == user  # Creador de l'esdeveniment
            or user.is_staff  # Staff de Django
        )

    def get_user_display_name(self):
        """Retorna el display_name de l'usuari si existeix, sinó el username."""
        if hasattr(self.user, "display_name") and self.user.display_name:
            return self.user.display_name
        return self.user.username

    def get_time_since(self):
        """
        Retorna el temps transcorregut des de la creació.
        Format: 'fa 2 minuts', 'fa 1 hora'
        """
        return f"fa {timesince(self.created_at)}"
