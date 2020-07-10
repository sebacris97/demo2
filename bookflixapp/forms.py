from django import forms
from django.core.exceptions import ValidationError
from .models import Autor, Editorial, Genero, Usuario, Comentario
from datetime import datetime as d
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User


from django.utils.translation import gettext_lazy as _


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Email',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su email',
        'autofocus': True, 'type': 'email', 'class': 'form-control',
        'id': 'id_email'}),
    )
    
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña',
               'class': 'form-control', 'autocomplete': 'current-password'}),
    )


        
class RegistrationForm(UserCreationForm):

    fecha_de_nacimiento = forms.DateField(required=True)
    tarjeta = forms.CharField(required=True, max_length=16, min_length=16)
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields['password2'].help_text = None

    def clean_email(self):
        data = self.cleaned_data["email"]
        try:
            user = User.objects.get(email=data)
        except User.DoesNotExist:
            return data
        raise ValidationError("El email ya esta registrado")


class CreateProfileForm(forms.Form):
    profilename = forms.CharField(required=True, label="Nombre de Perfil")


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('comentario',)
