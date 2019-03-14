from django.contrib import admin
from django.urls import path
from . import views

app_name='testing'

urlpatterns = [
    path('',views.ListViewMovies.as_view(), name='movieList'),

]
