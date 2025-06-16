from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction, OperationalError
from django.db.utils import DatabaseError
from .forms import UserRegisterForm, UserLoginForm, RecipeForm
from .models import Recipe, Like
import logging
import time

logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('recipe_list')
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

@login_required
def profile_view(request):
    user = request.user
    # Получаем все лайки пользователя
    user_likes = Like.objects.filter(user=user)
    # Получаем рецепты, которые пользователь лайкнул
    liked_recipes = Recipe.objects.filter(likes__in=user_likes).distinct()
    
    context = {
        'user': user,
        'liked_recipes': liked_recipes,
        'liked_recipes_count': user_likes.count()  # Используем количество лайков из модели Like
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@require_POST
def toggle_like(request, recipe_id):
    logger.info(f"Toggle like called for recipe {recipe_id} by user {request.user.id}")
    
    if not request.user.is_authenticated:
        logger.warning("Unauthenticated user tried to like recipe")
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    try:
        # Проверяем, что recipe_id является числом
        try:
            recipe_id = int(recipe_id)
        except (TypeError, ValueError):
            logger.error(f"Invalid recipe_id: {recipe_id}")
            return JsonResponse({'error': 'Invalid recipe ID'}, status=400)
        
        # Используем select_related для оптимизации запросов
        recipe = Recipe.objects.select_related('author').get(id=recipe_id)
        logger.info(f"Found recipe: {recipe.id}")
        
        with transaction.atomic():
            # Используем get_or_create для атомарной операции
            like, created = Like.objects.get_or_create(
                user=request.user,
                recipe=recipe,
                defaults={'user': request.user, 'recipe': recipe}
            )
            
            if not created:
                # Если лайк уже существовал - удаляем его
                like.delete()
                liked = False
                logger.info("Like removed")
            else:
                # Если лайк был создан
                liked = True
                logger.info("Like added")
            
            # Получаем обновленное количество лайков
            likes_count = recipe.likes.count()
            logger.info(f"Updated likes count: {likes_count}")
            
            response_data = {
                'liked': liked,
                'likes_count': likes_count
            }
            logger.info(f"Sending response: {response_data}")
            return JsonResponse(response_data)
                
    except Recipe.DoesNotExist:
        logger.error(f"Recipe {recipe_id} not found")
        return JsonResponse({'error': 'Recipe not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in toggle_like: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=400)
