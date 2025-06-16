from django.urls import path
from .views import (
    register_view, login_view, dashboard_view, logout_view,
    recipe_create_view, recipe_list_view, recipe_detail_view,
    profile_view, toggle_like
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('recipes/create/', recipe_create_view, name='recipe_create'),
    path('recipes/', recipe_list_view, name='recipe_list'),
    path('recipes/<int:recipe_id>/', recipe_detail_view, name='recipe_detail'),
    path('recipes/<int:recipe_id>/like/', toggle_like, name='toggle_like'),
]
