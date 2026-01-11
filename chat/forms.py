# Formularis del sistema de xat
from django import forms

from .models import ChatMessage

# Llista de paraules prohibides per la moderació
PARAULES_PROHIBIDES = [
    "idiota",
    "imbecil",
    "estupid",
    "merda",
    "cabro",
    "puta",
    "gilipolles",
    "capullo",
    "tonto",
    "subnormal",
]


class ChatMessageForm(forms.ModelForm):
    """
    Formulari per enviar missatges al xat.
    Inclou validacions per contingut buit, paraules ofensives i longitud màxima.
    """

    class Meta:
        model = ChatMessage
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Escriu el teu missatge...",
                    "maxlength": 500,
                }
            ),
        }

    def clean_message(self):
        """Validació personalitzada del missatge."""
        message = self.cleaned_data.get("message", "").strip()

        # Missatge no pot estar buit
        if not message:
            raise forms.ValidationError("El missatge no pot estar buit.")

        # Verificar longitud màxima
        if len(message) > 500:
            raise forms.ValidationError(
                "El missatge no pot tenir més de 500 caràcters."
            )

        # Detectar paraules ofensives
        message_lower = message.lower()
        for paraula in PARAULES_PROHIBIDES:
            if paraula in message_lower:
                raise forms.ValidationError(
                    "El missatge conté contingut inapropiat. "
                    "Si us plau, mantingues el respecte."
                )

        return message
