# URLs del sistema de xat
from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    # Enviar missatge: POST /chat/<event_pk>/send/
    path(
        "<int:event_pk>/send/",
        views.chat_send_message,
        name="send_message",
    ),
    # Carregar missatges: GET /chat/<event_pk>/messages/
    path(
        "<int:event_pk>/messages/",
        views.chat_load_messages,
        name="load_messages",
    ),
    # Eliminar missatge: POST /chat/message/<message_pk>/delete/
    path(
        "message/<int:message_pk>/delete/",
        views.chat_delete_message,
        name="delete_message",
    ),
    # Destacar missatge: POST /chat/message/<message_pk>/highlight/
    path(
        "message/<int:message_pk>/highlight/",
        views.chat_highlight_message,
        name="highlight_message",
    ),
]
