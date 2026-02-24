import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .services.llm_ollama import generate
from .services.prompts import build_prompt
from .services.retriever import retrieve_events


def chat_page(request):
    """Renderitza la pàgina principal del xat."""
    return render(request, "assistant_chat/chat.html")


@csrf_exempt
def chat_api(request):
    """Endpoint API que processa la lògica del xat."""
    if request.method != "POST":
        return JsonResponse({"error": "Només acceptem POST"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        message = (payload.get("message") or "").strip()
        only_future = bool(payload.get("only_future", True))
    except Exception:
        return JsonResponse({"error": "JSON no vàlid"}, status=400)

    if not message:
        return JsonResponse({"error": "El missatge està buit"}, status=400)

    # 1. Recuperem els esdeveniments candidats de la base de dades
    ranked = retrieve_events(message, only_future=only_future, k=8)

    # 2. Preparem les dades dels candidats per al prompt
    candidates = []
    for e, score in ranked:
        candidates.append(
            {
                "id": int(e.pk),
                "title": e.title,
                "scheduled_date": e.scheduled_date.isoformat()
                if e.scheduled_date
                else None,
                "category": e.category,
                "tags": e.tags or "",
                "url": e.get_absolute_url(),
                "score": round(float(score), 3),
            }
        )

    # 3. Generem la resposta amb la IA
    prompt = build_prompt(message, candidates)
    llm_text = generate(prompt)

    # 4. Intentem parsejar la resposta JSON de la IA
    try:
        llm_json = json.loads(llm_text)
    except Exception:
        # Si la IA falla i no dóna un JSON, fem un fallback de seguretat
        llm_json = {
            "answer": "Ho sento, he tingut un problema processant la resposta estructurada.",
            "recommended_ids": [c["id"] for c in candidates[:3]],
            "follow_up": "",
        }

    # 5. Validem que els IDs recomanats realment existeixen entre els candidats (anti-al·lucinació)
    allowed_ids = {c["id"] for c in candidates}
    final_ids = [i for i in llm_json.get("recommended_ids", []) if i in allowed_ids]

    final_events = [c for c in candidates if c["id"] in final_ids]

    return JsonResponse(
        {
            "answer": llm_json.get("answer", ""),
            "follow_up": llm_json.get("follow_up", ""),
            "events": final_events,
        }
    )
