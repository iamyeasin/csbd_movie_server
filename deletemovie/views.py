from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
from imdb import IMDb, helpers
from movies import models,forms
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from movies. models import UploadMovie,Category
from . import methods
import paramiko
import sys
import os
import re
from stat import S_ISDIR
from movies.forms import addMovieForm
import json,shutil
from settings.models import *
from django.core import serializers
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify
#####################################################
#
# host =  FTPDetails.objects.get(pk=1).server_address
# port = FTPDetails.objects.get(pk=1).portnumber
# username = FTPDetails.objects.get(pk=1).username
# password = FTPDetails.objects.get(pk=1).password
#

host = '103.83.15.87'
port = 22
username = 'cyber'
password ='intel12##'

# Base File
def index(request):
    return render(request, 'base.html')

def deleteMovies(request):

    # If the user is logged in then let him enter the page
    all_category = Category.objects.all()
    # for key,val in request.POST.items():
    #     print(key , " -> ",val)
    # # print(request.POST.get('search'))

    btnpressed = request.POST.get('search')
    if request.method == 'POST' and request.user.is_authenticated:

        form = addMovieForm(request.POST, request.FILES)
        ID = request.POST.get('movie_id')
        if ID:
            ID = ID.lstrip()
            ID = ID.rstrip()
        else:
            ID = ""
        # API_choosen = request.POST.get('APICategoryForMovie')
        title = request.POST.get('movie_title')
        year = request.POST.get('year')
        category = request.POST.get('categoryForMovie')
        api = request.POST.get('APICategoryForMovie')
        if api == 1:
            api = "IMDB"
        elif api == 2:
            api = "OMDB"
        else:
            api = "TMDB"

        # print(api,title,category,year)
        if btnpressed == "Search":
            try:
                if len(ID) > 0:
                    movie_info = UploadMovie.objects.get(movie_id=ID)
                else:
                    movie_info = UploadMovie.objects.get(movie_title=title,year=year,API_name=api)

                # print(movie_info.API_name)

                poster =  movie_info.poster_path
                destination_location = movie_info.destination_location


                if movie_info:
                    # list for director , writer, casts
                    form_IMDB = addMovieForm(initial={
                        'movie_title': movie_info.movie_title,
                        'movie_id': ID,
                        'year': movie_info.year,
                        'genre': movie_info.genre,
                        'IMDB_rating': float(movie_info.IMDB_rating),
                        'writer': movie_info.writer,
                        'director': movie_info.director,
                        'cast': movie_info.cast,
                        'plot': movie_info.plot,
                        #fix the category here
                        'moviecategory': movie_info.category_id,
                        'API_name': movie_info.API_name,
                        'is_converted' : movie_info.is_converted,
                        'is_featured' : movie_info.is_featured,
                    })

                    messages.success(request,"Desired data is found on the database")
                    return render(request, 'movies/delete_movies.html', {'dict': form_IMDB,
                                            'cats': all_category, 'poster':poster , 'moviecat':"English",
                                            'destination':destination_location })
            except:
                messages.error(request,"I am sorry, No data Found in the database")
                return render(request, 'movies/delete_movies.html', {'form': form, 'cats': all_category, })
        else:
            ID = request.POST.get('movie_id')
            try:

                try:
                    dlt = UploadMovie.objects.get(movie_id=ID)
                    
                    destination = dlt.destination_location
                    # destination = os.path.dirname(destination)
                    if( os.path.isdir(destination) ):
                        status = shutil.rmtree(destination)
                    dlt.delete() # deleting the row from database

                    return HttpResponse("Ok")
                except Exception as e:
                    return HttpResponseNotFound("cannot delete")
                    raise
            except:
                messages.error(request,"Couldn't delete the Data.")
                return render(request, 'movies/delete_movies.html', {'form': form, 'cats': all_category, })

    if request.user.is_authenticated:
        form = addMovieForm()  # just pass the form as a context
        return render(request, 'movies/delete_movies.html', {'form': form, 'cats': all_category, })
    else:
        return redirect('deletemovie:userlogin')
