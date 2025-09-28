from django.contrib.auth.models import AbstractUser
from djongo import models


class CustomUser(AbstractUser):
    # Classe d'usuari personalitzada que amplia la d'AbstractUser

    # Camps extra
    display_name = models.CharField(max_length=150, blank=True)  # Nom a mostrar
    bio = models.TextField(blank=True)  # Biografia de l'usuari
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True
    )  # Imatge de perfil
    # Necessita la llibreria Pillow instal·lada per a treballar amb imatges

    def __str__(self):
        return self.username  # Retorna el nom d'usuari com a representació


class Follow(models.Model):
    # Model que representa el seguiment entre usuaris
    # follower (A) segueix a following (B)

    follower = models.ForeignKey(
        "CustomUser",
        related_name="following_set",  # Usuaris que A està seguint
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        "CustomUser",
        related_name="followers_set",  # Usuaris que segueixen a B
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Data i hora del seguiment

    class Meta:
        unique_together = ("follower", "following")  # Evita duplicats A->B

    def __str__(self):
        return f"{self.follower} -> {self.following}"  # Mostra la relació A -> B
