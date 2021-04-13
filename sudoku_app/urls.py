from django.urls import path, include
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='puzzles/', permanent=True)),
    path('puzzles/', views.puzzles, name='puzzles'),
    path('puzzles/create/<str:difficulty>/', views.create_puzzle, name='create_puzzle'),
    path('puzzles/<int:puzzle_id>/', views.puzzle, name='puzzle'),
    path('puzzles/<int:puzzle_id>/save', views.save_puzzle, name='save_puzzle'),
    path('puzzles/<int:puzzle_id>/check', views.check_puzzle, name='check_puzzle'),
    path('puzzles/<int:puzzle_id>/hint', views.add_hint, name='add_hint'),
    path('puzzles/<int:puzzle_id>/delete', views.delete_puzzle, name='delete_puzzle'),
    path('puzzles/<int:puzzle_id>/reset', views.reset_puzzle, name='reset_puzzle'),
    path('puzzles/statistics', views.display_stats, name='display_stats'),
    path('puzzles/leaderboard', views.display_leaderboard, name='display_leaderboard'),
    path('createuser/', views.create_user, name='create_user'),
]