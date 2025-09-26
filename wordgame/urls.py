from django.urls import path
from game import views
from django.contrib import admin

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('game/', views.start_game, name='start_game'),
    path('guess/<int:game_id>/', views.submit_guess, name='submit_guess'),
    path('admin/', admin.site.urls),
    path('hint/<int:game_id>/', views.get_hint, name='get_hint'),
    path('daily-report/', views.daily_report, name='daily_report'),
    path('user-report/', views.user_report, name='user_report'),
]