from django.utils import timezone

from events.models import Event
from semantic_search.services.embeddings import embed_text
from semantic_search.services.ranker import cosine_top_k


def build_event_text(e: Event) -> str:
    # Construeix un text únic combinant els camps importants de l'esdeveniment
    return " | ".join(
        [
            (e.title or "").strip(),
            (e.description or "").strip(),
            (e.category or "").strip(),
            (e.tags or "").strip(),
        ]
    ).strip()


def retrieve_events(query: str, only_future: bool = True, k: int = 8):
    # 1. Obtenim l'embedding de la consulta de l'usuari
    q_vec = embed_text(query)

    # 2. Agafem tots els esdeveniments i filtrem per data si cal
    qs = Event.objects.all()
    if only_future:
        qs = qs.filter(scheduled_date__gte=timezone.now())

    items = []
    # 3. Optimització: només carreguem de la BD els camps que necessitem
    for e in qs.only("id", "title", "scheduled_date", "category", "tags", "embedding"):
        emb = getattr(e, "embedding", None)
        if isinstance(emb, list) and len(emb) > 0:
            items.append((e, emb))

    # 4. Calculem la similitud i ordenem els resultats
    ranked = cosine_top_k(q_vec, items, k=max(k, 20))

    # 5. Llindar mínim per evitar recomanar coses sense sentit
    ranked = [(e, s) for (e, s) in ranked if s >= 0.25]

    # 6. Retornem el top K
    return ranked[:k]
