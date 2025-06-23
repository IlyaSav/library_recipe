from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction, OperationalError
from django.db.utils import DatabaseError
from .forms import UserRegisterForm, UserLoginForm, RecipeForm, CommentForm, ArticleForm
from .models import Recipe, Like, Comment, Favorite, Category, Article
from .templatetags.custom_filters import censor
import logging
import time
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.db import models
from django.db.models import Q, Avg, Count
from django.contrib.admin.views.decorators import staff_member_required
import random
from datetime import datetime, timedelta

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
def profile_view(request):
    user = request.user
    # Получаем все лайки пользователя
    user_likes = Like.objects.filter(user=user)
    # Получаем рецепты, которые пользователь лайкнул
    liked_recipes = Recipe.objects.filter(likes__in=user_likes).distinct()
    
    # Получаем избранные рецепты
    favorite_recipes = Recipe.objects.filter(favorited_by__user=user).distinct()
    
    context = {
        'user': user,
        'liked_recipes': liked_recipes,
        'liked_recipes_count': user_likes.count(),
        'favorite_recipes': favorite_recipes,
        'favorite_recipes_count': favorite_recipes.count()
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.instructions = form.cleaned_data['steps']
            recipe.save()
            form.save_m2m()  # Сохраняем связи many-to-many (категории)
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
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category')
    min_rating = request.GET.get('min_rating')

    if search_query:
        recipes = recipes.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(instructions__icontains=search_query)
        )

    selected_category_name = None
    if category_id:
        recipes = recipes.filter(categories__id=category_id)
        cat = Category.objects.filter(id=category_id).first()
        if cat:
            selected_category_name = cat.name

    # Аннотируем средний рейтинг и фильтруем по нему
    recipes = recipes.annotate(avg_rating=Avg('comments__rating'))
    if min_rating:
        try:
            min_rating_value = int(min_rating)
            recipes = recipes.filter(avg_rating__gte=min_rating_value)
        except ValueError:
            pass

    categories = Category.objects.all()

    context = {
        'recipes': recipes,
        'categories': categories,
        'selected_category': str(category_id) if category_id else None,
        'selected_category_name': selected_category_name,
        'search_query': search_query,
        'min_rating': min_rating,
    }
    return render(request, 'accounts/recipe_list.html', context)

@never_cache
@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    instructions_list = recipe.instructions.splitlines() if recipe.instructions else []
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.text = censor(comment.text)
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен.')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        form = CommentForm()
    
    comments = Comment.objects.filter(recipe=recipe).order_by('-created_at')
    for comment in comments:
        comment.text = censor(comment.text)
    
    is_liked = False
    is_favorited = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, recipe=recipe).exists()
        is_favorited = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
    
    context = {
        'recipe': recipe,
        'instructions_list': instructions_list,
        'user': request.user,
        'form': form,
        'comments': comments,
        'is_liked': is_liked,
        'likes_count': recipe.likes.count(),
        'is_favorited': is_favorited,
        'favorites_count': recipe.favorited_by.count()
    }
    return render(request, 'accounts/recipe_detail.html', context)

@login_required
def recipe_edit_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    # Проверяем, является ли пользователь автором рецепта
    if request.user != recipe.author:
        messages.error(request, 'У вас нет прав для редактирования этого рецепта.')
        return redirect('recipe_detail', recipe_id=recipe.id)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.instructions = form.cleaned_data['steps']
            recipe.save()
            form.save_m2m()  # Сохраняем связи many-to-many (категории)
            messages.success(request, 'Рецепт успешно обновлен.')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        # Инициализируем форму с данными рецепта
        initial_data = {
            'title': recipe.title,
            'description': recipe.description,
            'ingredients': recipe.ingredients,
            'steps': recipe.instructions,
            'prep_time': recipe.prep_time,
            'cook_time': recipe.cook_time,
        }
        form = RecipeForm(instance=recipe, initial=initial_data)
    
    return render(request, 'accounts/recipe_edit.html', {
        'form': form,
        'recipe': recipe
    })

def logout_view(request):
    logout(request)
    return redirect('login')

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

def recipe_delete_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user != recipe.author:
        messages.error(request, 'У вас нет прав для удаления этого рецепта.')
        return redirect('recipe_detail', recipe_id=recipe.id)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Рецепт успешно удалён.')
        return redirect('recipe_list')
    return render(request, 'accounts/recipe_confirm_delete.html', {'recipe': recipe})

@login_required
@require_POST
def toggle_favorite(request, recipe_id):
    logger.info(f"Toggle favorite called for recipe {recipe_id} by user {request.user.id}")
    
    if not request.user.is_authenticated:
        logger.warning("Unauthenticated user tried to favorite recipe")
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    
    try:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        logger.info(f"Found recipe: {recipe.id}")
        
        with transaction.atomic():
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                recipe=recipe,
                defaults={'user': request.user, 'recipe': recipe}
            )
            
            if not created:
                favorite.delete()
                is_favorited = False
                logger.info("Favorite removed")
            else:
                is_favorited = True
                logger.info("Favorite added")
            
            favorites_count = recipe.favorited_by.count()
            logger.info(f"Updated favorites count: {favorites_count}")
            
            response_data = {
                'is_favorited': is_favorited,
                'favorites_count': favorites_count
            }
            logger.info(f"Sending response: {response_data}")
            return JsonResponse(response_data)
                
    except Recipe.DoesNotExist:
        logger.error(f"Recipe {recipe_id} not found")
        return JsonResponse({'error': 'Recipe not found'}, status=404)
    except Exception as e:
        logger.error(f"Error in toggle_favorite: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def like_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)
    
    if not created:
        like.delete()
    
    return redirect('recipe_detail', recipe_id=recipe_id)

@login_required
def favorite_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    
    if not created:
        favorite.delete()
    
    return redirect('recipe_detail', recipe_id=recipe_id)

def articles_list_view(request):
    articles = Article.objects.select_related('author').order_by('-created_at')
    return render(request, 'accounts/articles_list.html', {'articles': articles})

@staff_member_required
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Статья успешно создана!')
            return redirect('articles_list')
    else:
        form = ArticleForm()
    return render(request, 'accounts/article_create.html', {'form': form})

@login_required
def menu_for_week_view(request):
    user = request.user
    # Получаем рецепты, которые пользователь лайкал или добавил в избранное
    liked_recipes = Recipe.objects.filter(likes__user=user)
    favorite_recipes = Recipe.objects.filter(favorited_by__user=user)
    user_recipes = (liked_recipes | favorite_recipes).distinct()

    if user_recipes.exists():
        recipes_qs = user_recipes
    else:
        # Если пользователь не проявлял активности — топ-лайкнутые рецепты
        recipes_qs = Recipe.objects.annotate(likes_count=Count('likes')).order_by('-likes_count', '-created_at')[:20]

    recipes_list = list(recipes_qs)
    random.shuffle(recipes_list)
    week_menu = recipes_list[:7]

    # Для отображения дней недели
    days = [
        'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ]
    menu = list(zip(days, week_menu))

    return render(request, 'accounts/menu_for_week.html', {'menu': menu, 'has_user_activity': user_recipes.exists()})
