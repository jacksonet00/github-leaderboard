from django.contrib import admin
from .models import Result, Leaderboard, Commit

# Register your models here.

admin.site.register(Result)
admin.site.register(Leaderboard)
admin.site.register(Commit)
