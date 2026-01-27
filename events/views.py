from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import EventCreationForm, EventSearchForm, EventUpdateForm
from .models import Event


def event_list_view(request):
    search_form = EventSearchForm(request.GET)
    events = Event.objects.all().order_by("-is_featured", "-created_at")

    if search_form.is_valid():
        search_query = search_form.cleaned_data.get("search")
        category = search_form.cleaned_data.get("category")
        status = search_form.cleaned_data.get("status")
        date_from = search_form.cleaned_data.get("date_from")
        date_to = search_form.cleaned_data.get("date_to")

        if search_query:
            events = events.filter(title__icontains=search_query)
        if category:
            events = events.filter(category=category)
        if status:
            events = events.filter(status=status)
        if date_from:
            events = events.filter(scheduled_date__date__gte=date_from)
        if date_to:
            events = events.filter(scheduled_date__date__lte=date_to)

    paginator = Paginator(events, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_form": search_form,
    }
    return render(request, "events/event_list.html", context)


def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    from chat.forms import ChatMessageForm

    context = {
        "event": event,
        "chat_form": ChatMessageForm(),
    }
    return render(request, "events/event_detail.html", context)


@login_required
def event_create_view(request):
    if request.method == "POST":
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            messages.success(request, "Esdeveniment creat correctament!")
            return redirect("events:event_detail", pk=event.pk)
        else:
            messages.error(request, "Hi ha errors al formulari.")
    else:
        form = EventCreationForm()

    context = {"form": form, "title": "Crear Esdeveniment"}
    return render(request, "events/event_form.html", context)


@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.creator != request.user:
        messages.error(request, "No tens permís per editar aquest esdeveniment.")
        return redirect("events:event_detail", pk=pk)

    if request.method == "POST":
        form = EventUpdateForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Esdeveniment actualitzat correctament!")
            return redirect("events:event_detail", pk=event.pk)
        else:
            messages.error(request, "Hi ha errors al formulari.")
    else:
        form = EventUpdateForm(instance=event)

    context = {"form": form, "title": "Editar Esdeveniment", "event": event}
    return render(request, "events/event_form.html", context)


@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.creator != request.user:
        messages.error(request, "No tens permís per eliminar aquest esdeveniment.")
        return redirect("events:event_detail", pk=pk)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Esdeveniment eliminat correctament!")
        return redirect("events:event_list")

    context = {"event": event}
    return render(request, "events/event_confirm_delete.html", context)


@login_required
def my_events_view(request):
    events = Event.objects.filter(creator=request.user).order_by("-created_at")

    status_filter = request.GET.get("status")
    if status_filter:
        events = events.filter(status=status_filter)

    context = {"events": events, "current_filter": status_filter}
    return render(request, "events/my_events.html", context)


def events_by_category_view(request, category):
    # Validate category exists in choices
    valid_categories = [c[0] for c in Event.CATEGORY_CHOICES]
    if category not in valid_categories:
        messages.error(request, "Categoria no vàlida.")
        return redirect("events:event_list")

    events = Event.objects.filter(category=category).order_by("-created_at")

    paginator = Paginator(events, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "category": category,
        "category_name": dict(Event.CATEGORY_CHOICES).get(category),
    }
    return render(request, "events/event_list.html", context)
