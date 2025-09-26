from django.contrib import admin
from .models import Game, Word
from django.db.models import Count, Q  # Added Q import
from django.utils import timezone

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'secret_word', 'won')

    def changelist_view(self, request, extra_context=None):
        # Daily report: For today (or any day, but default today)
        today = timezone.now().date()
        daily_users = Game.objects.filter(date=today).values('user').distinct().count()
        daily_correct = Game.objects.filter(date=today, won=True).count()
        
        # Per-user report: Aggregate over all dates
        user_stats = Game.objects.values('user__username', 'date').annotate(
            tried=Count('id'), correct=Count('won', filter=Q(won=True))  # Use Q instead of models.Q
        ).order_by('user__username', 'date')
        
        extra_context = extra_context or {}
        extra_context['daily_users'] = daily_users
        extra_context['daily_correct'] = daily_correct
        extra_context['user_stats'] = user_stats
        return super().changelist_view(request, extra_context=extra_context)