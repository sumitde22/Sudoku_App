from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class SudokuGame(models.Model):
    DIFFICULTIES = [
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard')
    ]
    initial_board = models.CharField(max_length=500)
    current_board = models.CharField(max_length=500)
    solution_board = models.CharField(max_length=500)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
    
    def is_solved(self):
        return self.current_board == self.solution_board

class SudokuRecord(models.Model):
    DIFFICULTIES = [
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard')
    ]
    puzzle_id = models.IntegerField(primary_key=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTIES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    



