from django.contrib import admin
from django.urls import path
from . import views,methods

app_name='deletemovie'

urlpatterns = [
    path('',views.deleteMovies, name='deleteMovies'),
    path('login/',methods.userLogin, name='userlogin'),
    path('logout/',methods.userLogout, name='userlogout'),

]
