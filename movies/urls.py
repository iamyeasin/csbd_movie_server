from django.contrib import admin
from django.urls import path
from . import views,methods

app_name='movies'

urlpatterns = [
    path('',views.index, name='index'),
    path('login/',methods.userLogin, name='userlogin'),
    path('logout/',methods.userLogout, name='userlogout'),
    path('add_movies/',views.addMovies, name='addmovies'),
    path('manual_upload_movie/',views.manualUpload, name='manualmovieupload'),
    path('update_movie/',views.UpdateMovie, name='updatemovie'),
    path('search_movies/',views.ListViewMovies.as_view(), name='searchmovies'),
    path('possible_search/',views.possibleSearch.as_view(), name='possiblesearch'),
]
