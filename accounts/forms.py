from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Recipe, Comment, Article

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput(attrs={'autocomplete': 'given-name'}))
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput(attrs={'autocomplete': 'family-name'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()  # Важно вызывать родительский clean
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Пароли не совпадают.')
        return cleaned_data

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        import re
        errors = []
        if len(password or '') < 8:
            errors.append('Пароль должен быть не менее 8 символов.')
        if len(re.findall(r'[A-Za-z]', password or '')) < 2:
            errors.append('Пароль должен содержать минимум две английские буквы.')
        if errors:
            raise forms.ValidationError(errors)
        return password

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'username'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

class RecipeForm(forms.ModelForm):
    title = forms.CharField(
        label='Название рецепта',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите название рецепта'
        })
    )
    
    description = forms.CharField(
        label='Описание',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Опишите ваш рецепт'
        })
    )
    
    ingredients = forms.CharField(
        label='Ингредиенты',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите каждый ингредиент с новой строки\nНапример:\n- 200г муки\n- 2 яйца\n- 100мл молока'
        })
    )
    
    steps = forms.CharField(
        label='Шаги приготовления',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 7,
            'placeholder': 'Введите каждый шаг с новой строки\nНапример:\n1. Смешать сухие ингредиенты\n2. Добавить яйца и молоко\n3. Замесить тесто'
        })
    )
    
    prep_time = forms.IntegerField(
        label='Время подготовки (минут)',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: 15'
        })
    )
    
    cook_time = forms.IntegerField(
        label='Время приготовления (минут)',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: 30'
        })
    )
    
    image = forms.ImageField(
        label='Фото блюда',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    categories = forms.ModelMultipleChoiceField(
        label='Категории',
        queryset=Recipe.categories.field.related_model.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '5'
        })
    )

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'steps', 'prep_time', 'cook_time', 'image', 'categories']

    def clean_ingredients(self):
        ingredients = self.cleaned_data['ingredients']
        # Разбиваем на строки и удаляем пустые строки
        ingredients_list = [ing.strip() for ing in ingredients.split('\n') if ing.strip()]
        if not ingredients_list:
            raise forms.ValidationError('Добавьте хотя бы один ингредиент')
        return ingredients

    def clean_steps(self):
        steps = self.cleaned_data['steps']
        # Разбиваем на строки и удаляем пустые строки
        steps_list = [step.strip() for step in steps.split('\n') if step.strip()]
        if not steps_list:
            raise forms.ValidationError('Добавьте хотя бы один шаг приготовления')
        return steps

    def save(self, commit=True):
        recipe = super().save(commit=commit)
        return recipe

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...'
            }),
            # rating без виджета, чтобы кастомно отрисовать звёзды
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Тема статьи'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Текст статьи', 'rows': 8}),
        }

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    first_name = forms.CharField(required=True, label='Имя', widget=forms.TextInput(attrs={'autocomplete': 'given-name'}))
    last_name = forms.CharField(required=True, label='Фамилия', widget=forms.TextInput(attrs={'autocomplete': 'family-name'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
