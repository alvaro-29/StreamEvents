# Vistes del sistema de xat (API JSON)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from events.models import Event

from .forms import ChatMessageForm
from .models import ChatMessage


@login_required
@require_POST
def chat_send_message(request, event_pk):
    """
    Envia un missatge al xat d'un esdeveniment.
    Només funciona si l'esdeveniment està en directe.
    """
    event = get_object_or_404(Event, pk=event_pk)

    # Verificar que l'esdeveniment està en directe
    if event.status != "live":
        return JsonResponse(
            {
                "success": False,
                "error": "El xat només està disponible durant l'esdeveniment en directe.",
            },
            status=400,
        )

    # Processar el formulari
    form = ChatMessageForm(request.POST)
    if form.is_valid():
        # Crear missatge sense guardar encara
        message = form.save(commit=False)
        message.user = request.user
        message.event = event
        message.save()

        # Retornar dades del missatge creat
        return JsonResponse(
            {
                "success": True,
                "message": {
                    "id": message.id,
                    "user": message.user.username,
                    "display_name": message.get_user_display_name(),
                    "message": message.message,
                    "created_at": message.get_time_since(),
                    "can_delete": message.can_delete(request.user),
                    "is_highlighted": message.is_highlighted,
                },
            }
        )

    # Retornar errors de validació
    return JsonResponse(
        {"success": False, "errors": form.errors},
        status=400,
    )


def chat_load_messages(request, event_pk):
    """
    Carrega els últims 50 missatges d'un esdeveniment.
    No requereix autenticació per permetre visualització.
    """
    event = get_object_or_404(Event, pk=event_pk)

    # Obtenir missatges ordenats per data
    # Nota: Djongo té problemes amb is_deleted=False (NOT operator)
    # Per això filtrem tots els missatges i excloem els eliminats en Python
    all_messages = ChatMessage.objects.filter(
        event=event,
    ).order_by("created_at")

    # Crear llista de diccionaris amb les dades (només no eliminats)
    messages_list = []
    count = 0
    for msg in all_messages:
        # Filtrar eliminats en Python per evitar problemes amb Djongo
        if msg.is_deleted:
            continue
        if count >= 50:
            break
        messages_list.append(
            {
                "id": msg.id,
                "user": msg.user.username,
                "display_name": msg.get_user_display_name(),
                "message": msg.message,
                "created_at": msg.get_time_since(),
                "can_delete": msg.can_delete(request.user)
                if request.user.is_authenticated
                else False,
                "is_highlighted": msg.is_highlighted,
            }
        )
        count += 1

    return JsonResponse({"messages": messages_list})


@login_required
@require_POST
def chat_delete_message(request, message_pk):
    """
    Elimina un missatge (soft delete).
    Només pot eliminar: creador del missatge, creador de l'event, o staff.
    """
    message = get_object_or_404(ChatMessage, pk=message_pk)

    # Verificar permisos
    if not message.can_delete(request.user):
        return JsonResponse(
            {
                "success": False,
                "error": "No tens permisos per eliminar aquest missatge.",
            },
            status=403,
        )

    # Soft delete
    message.is_deleted = True
    message.save()

    return JsonResponse({"success": True})


@login_required
@require_POST
def chat_highlight_message(request, message_pk):
    """
    Destaca o des-destaca un missatge (toggle).
    Només pot fer-ho el creador de l'esdeveniment.
    """
    message = get_object_or_404(ChatMessage, pk=message_pk)

    # Verificar que l'usuari és el creador de l'esdeveniment
    if message.event.creator != request.user:
        return JsonResponse(
            {
                "success": False,
                "error": "Només el creador de l'esdeveniment pot destacar missatges.",
            },
            status=403,
        )

    # Toggle is_highlighted
    message.is_highlighted = not message.is_highlighted
    message.save()

    return JsonResponse(
        {
            "success": True,
            "is_highlighted": message.is_highlighted,
        }
    )
