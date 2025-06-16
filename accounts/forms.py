from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Recipe

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'steps', 'prep_time', 'cook_time', 'image', 'categories']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'ingredients': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите каждый продукт с новой строки'}),
            'steps': forms.Textarea(attrs={'rows': 7, 'placeholder': 'Введите каждый шаг с новой строки. Шаги будут автоматически пронумерованы.'}),
            'categories': forms.SelectMultiple(),
        }
