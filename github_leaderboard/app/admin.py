from django.contrib import admin

from .models import Commit, Leaderboard, Result

# Register your models here.

admin.site.register(Result)
admin.site.register(Leaderboard)
admin.site.register(Commit)
