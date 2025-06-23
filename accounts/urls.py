from django.urls import path
from . import views
from .views import articles_list_view, article_create_view, menu_for_week_view

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('recipes/create/', views.recipe_create_view, name='recipe_create'),
    path('recipes/', views.recipe_list_view, name='recipe_list'),
    path('recipes/<int:recipe_id>/', views.recipe_detail_view, name='recipe_detail'),
    path('recipes/<int:recipe_id>/edit/', views.recipe_edit_view, name='recipe_edit'),
    path('recipes/<int:recipe_id>/like/', views.toggle_like, name='toggle_like'),
    path('recipes/<int:recipe_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('recipes/<int:recipe_id>/delete/', views.recipe_delete_view, name='recipe_delete'),
    path('recipe/<int:recipe_id>/like/', views.like_recipe, name='like_recipe'),
    path('recipe/<int:recipe_id>/favorite/', views.favorite_recipe, name='favorite_recipe'),
    path('articles/', articles_list_view, name='articles_list'),
    path('articles/create/', article_create_view, name='article_create'),
    path('menu-for-week/', menu_for_week_view, name='menu_for_week'),
]
