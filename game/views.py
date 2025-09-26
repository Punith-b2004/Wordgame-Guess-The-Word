from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Game, Word
from django.utils import timezone
from django.db.models import Count, Q
import random
from django.db.models import Count
from django.contrib.auth.models import User  
from django.utils.dateparse import parse_date


def home(request):
    max_limit_reached = False
    if request.user.is_authenticated:
        max_limit_reached = not Game.can_play_today(request.user)
    return render(request, 'home.html', {'max_limit_reached': max_limit_reached})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:  
                return redirect('/admin/')
            else:  
                return redirect('start_game')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')  

def get_hint(request, game_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        game = get_object_or_404(Game, id=game_id, user=request.user)
        secret = game.secret_word
        if not secret or len(secret) != 5:
            return JsonResponse({'error': 'Invalid game state'}, status=400)
        
        
        guessed_letters = set()
        for g in game.guesses:
            guessed_letters.update(g['guess'])
        
        unused_letters = [letter for letter in secret if letter not in guessed_letters]
        if not unused_letters:
            return JsonResponse({'error': 'No hints left—all letters revealed!'})
        
        hint = random.choice(unused_letters)  
        return JsonResponse({'hint': f"The secret word contains '{hint}'"})
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    




def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def daily_report(request):
    date_str = request.GET.get('date', timezone.now().date().isoformat())  # Default to today if empty
    date = parse_date(date_str)
    if date is None:
        date = timezone.now().date()  # Fallback to today if parsing fails
    users = Game.objects.filter(date=date).values('user').distinct().count()
    correct = Game.objects.filter(date=date, won=True).count()
    return render(request, 'daily_report.html', {'date': date, 'users': users, 'correct': correct})

@login_required
@user_passes_test(is_admin)
def user_report(request):
    users = User.objects.all()
    selected_user = None
    user_games = []

    username = request.GET.get('username')
    if username:
        selected_user = get_object_or_404(User, username=username)
        user_games = Game.objects.filter(user=selected_user).values('date').annotate(
            tried=Count('id'),
            correct=Count('won', filter=Q(won=True))
        )
    else:
        if users.exists():
            selected_user = users.first()
            user_games = Game.objects.filter(user=selected_user).values('date').annotate(
                tried=Count('id'),
                correct=Count('won', filter=Q(won=True))
            )

    return render(request, 'user_report.html', {
        'users': users,
        'selected_user': selected_user,
        'user_games': user_games
    })

def start_game(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not Game.can_play_today(request.user):
        return render(request, 'game.html', {'message': 'You have reached the daily limit of 3 games.'})
    
    secret_word = Word.get_random_word()
    if not secret_word:
        return render(request, 'game.html', {'message': 'No words available.'})
    
    game = Game.objects.create(user=request.user, secret_word=secret_word)
    return render(request, 'game.html', {'game_id': game.id, 'guesses': []})

def submit_guess(request, game_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        game = get_object_or_404(Game, id=game_id, user=request.user)
        if request.method == 'POST':
            guess = request.POST.get('guess')
            if not guess:
                return JsonResponse({'error': 'No guess provided'}, status=400)
            guess = guess.upper()
            if len(guess) != 5 or not guess.isalpha():
                return JsonResponse({'error': 'Invalid guess'}, status=400)
            
            if game.add_guess(guess):
                if game.won or len(game.guesses) == 5:
                    message = 'Congratulations! You won!' if game.won else 'Better luck next time!'
                    return JsonResponse({'guesses': game.guesses, 'message': message, 'game_over': True})
                return JsonResponse({'guesses': game.guesses})
            return JsonResponse({'error': 'Max guesses reached'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)