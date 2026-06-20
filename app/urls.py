from django.urls import path
from . import views

urlpatterns = [
 
    path('home',              views.home,          name='home'),
    path('app/',          views.index,         name='index'),
    path('detect/',       views.detect_emotion, name='detect_emotion'),
    path('search_songs/', views.search_songs,   name='search_songs'),
    path('search_songs_by_name/', views.search_songs_by_name, name='search_songs_by_name'),

 
    path('auth/',             views.auth_view,            name='auth'),
    path('register/',         views.register_view,        name='register'),
    path('',            views.login_view,           name='login'),
    path('logout/',           views.logout_view,          name='logout'),
    path('forgot-password/',  views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
]
