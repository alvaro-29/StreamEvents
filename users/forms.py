# Importem els mòduls necessaris de Django per formularis i validacions
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

# Obtenim el model d'usuari personalitzat
User = get_user_model()


# Formulari de creació de nou usuari
class CustomUserCreationForm(forms.ModelForm):
    # Camps especials per contrasenya i confirmació
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        # Assignem el model i els camps que volem mostrar al formulari
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    # Validació de l'email: ha de ser únic
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Aquest email ja està registrat.")
        return email

    # Validació del username: només caràcters vàlids
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match(r"^[\w.@+-]+$", username):
            raise ValidationError(
                "El username només pot contenir lletres, números i @/./+/-/_"
            )
        return username

    # Validació de les contrasenyes
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        # Comprovem que coincideixin
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les contrasenyes no coincideixen.")
        # Comprovem la longitud mínima
        if len(password1) < 8:
            raise ValidationError("La contrasenya ha de tenir almenys 8 caràcters.")
        return password2

    # Sobrescrivim el mètode save per guardar la contrasenya amb hash
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# Formulari per actualitzar el perfil d'un usuari existent
class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "display_name", "bio", "avatar"]
        # Widgets personalitzats per bio i avatar
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "avatar": forms.FileInput(),
        }


# Formulari d'autenticació personalitzat per login amb email o username
class CustomAuthenticationForm(AuthenticationForm):
    # Reescrivim el camp username per acceptar email
    username = forms.CharField(label="Username or Email")

    # Validació del formulari
    def clean(self):
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username_or_email and password:
            try:
                # Intentem obtenir l'usuari per email
                user = User.objects.get(email=username_or_email)
                # Si existeix, assignem el username real al formulari
                self.cleaned_data["username"] = user.username
            except User.DoesNotExist:
                # Si no existeix, deixem que el formulari original gestioni l'error
                pass
        return super().clean()
