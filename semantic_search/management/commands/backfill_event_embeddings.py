from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event
from semantic_search.services.embeddings import embed_text, model_name


class Command(BaseCommand):
    help = "Genera i desa embeddings per a Events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recalcula encara que ja hi hagi embedding",
        )
        parser.add_argument(
            "--limit", type=int, default=0, help="Limita el nombre d'events (0 = tots)"
        )

    def handle(self, *args, **options):
        limit = options["limit"]

        self.stdout.write("Iniciant la generació d'embeddings...")

        # Això és vital perquè Djongo no intenti llegir 'embedding'
        qs = (
            Event.objects.all()
            .order_by("created_at")
            .only("id", "title", "description", "category", "tags", "created_at")
        )

        if limit and limit > 0:
            qs = qs[:limit]

        total = 0
        for e in qs:
            text_parts = [
                (e.title or "").strip(),
                (e.description or "").strip(),
                (str(e.category) or "").strip(),
            ]

            # Comprovem tags de manera segura
            if hasattr(e, "tags") and e.tags:
                text_parts.append(str(e.tags))

            full_text = " | ".join([p for p in text_parts if p]).strip()

            if not full_text:
                continue

            # Generem el vector
            vec = embed_text(full_text)

            # Assignem el valor
            e.embedding = vec
            e.embedding_model = model_name()
            e.embedding_updated_at = timezone.now()

            # Guardem només els camps nous a la BD
            e.save(
                update_fields=["embedding", "embedding_model", "embedding_updated_at"]
            )
            total += 1

            if total % 10 == 0:
                self.stdout.write(f"Processats: {total}...")

        self.stdout.write(
            self.style.SUCCESS(f"Finalitzat! Embeddings generats: {total}")
        )
