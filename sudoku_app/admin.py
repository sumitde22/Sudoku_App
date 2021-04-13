from django.contrib import admin

from .models import SudokuGame
from .models import SudokuRecord

# Register your models here.

admin.site.register(SudokuGame)
admin.site.register(SudokuRecord)

