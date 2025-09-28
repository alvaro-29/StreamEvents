from django.contrib import admin
# Importem les eines per gestionar models des del panell d’administració
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Follow


@admin.register(CustomUser)  # Registra el model CustomUser al panell d’admin
class CustomUserAdmin(UserAdmin):
    # Afegim els camps extra (display_name, bio, avatar) a la configuració de l’usuari
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("display_name", "bio", "avatar")}),
    )
    # Columnes que es mostren a la llista d’usuaris
    list_display = ("username", "email", "display_name", "is_staff", "is_active")
    # Camps pels quals es pot buscar des del panell
    search_fields = ("username", "email", "display_name")


@admin.register(Follow)  # Registra el model Follow al panell d’admin
class FollowAdmin(admin.ModelAdmin):
    # Columnes que es mostren a la llista de relacions de seguiment
    list_display = ("follower", "following", "created_at")
    # Permet buscar per nom d’usuari del follower i del following
    search_fields = ("follower__username", "following__username")
    # Permet filtrar les relacions segons la data de creació
    list_filter = ("created_at",)
