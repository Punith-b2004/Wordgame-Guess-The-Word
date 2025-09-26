from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class Word(models.Model):
    word = models.CharField(max_length=5, unique=True)  # 5-letter uppercase word

    @classmethod
    def get_random_word(cls):
        words = cls.objects.all()
        if words.exists():
            return random.choice(words).word
        return None

class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    secret_word = models.CharField(max_length=5)
    date = models.DateField(default=timezone.now)
    won = models.BooleanField(default=False)
    guesses = models.JSONField(default=list)  # Store list of guesses and feedback

    def add_guess(self, guess):
        if len(self.guesses) >= 5:
            return False
        feedback = []
        for i in range(5):
            if guess[i] == self.secret_word[i]:
                feedback.append('green')
            elif guess[i] in self.secret_word:
                feedback.append('orange')
            else:
                feedback.append('gray')
        self.guesses.append({'guess': guess, 'feedback': feedback})
        if guess == self.secret_word:
            self.won = True
        self.save()
        return True

    @classmethod
    def can_play_today(cls, user):
        today = timezone.now().date()
        games_today = cls.objects.filter(user=user, date=today).count()
        return games_today < 3