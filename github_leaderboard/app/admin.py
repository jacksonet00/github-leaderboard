from django.contrib import admin
from .models import ExtendedUser, Result, Leaderboard, Commit

# Register your models here.

admin.site.register(ExtendedUser)
admin.site.register(Result)
admin.site.register(Leaderboard)
admin.site.register(Commit)
