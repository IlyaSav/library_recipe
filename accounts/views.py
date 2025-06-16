from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, RecipeForm
from .models import Recipe

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.instructions = form.cleaned_data['steps']
            recipe.save()
            messages.success(request, 'Рецепт успешно создан.')
            return redirect('recipe_list')
        else:
            messages.error(request, 'Ошибка при создании рецепта. Пожалуйста, проверьте форму.')
            return render(request, 'accounts/recipe_create.html', {'form': form})
    else:
        form = RecipeForm()
    return render(request, 'accounts/recipe_create.html', {'form': form})

@login_required
def recipe_list_view(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'accounts/recipe_list.html', {'recipes': recipes})

@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    instructions_list = recipe.instructions.splitlines() if recipe.instructions else []
    return render(request, 'accounts/recipe_detail.html', {'recipe': recipe, 'instructions_list': instructions_list})

def logout_view(request):
    logout(request)
    return redirect('login')
