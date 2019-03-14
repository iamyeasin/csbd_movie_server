from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponseNotFound, Http404, HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
from imdb import IMDb, helpers
import re, datetime
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from . models import *
from . forms import *
from . import methods
import json,imdb,re,os,sys,paramiko
import tmdbsimple as tmdb
from imdb import IMDb, helpers
import omdb
from django.views.generic import TemplateView,ListView,CreateView,DeleteView
from django.core import serializers
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify
from . filters import MovieFilter
from settings.models import *
from movies.methods import get_IMDB_by_Name,get_TMDB_by_Name
from imdb import IMDb, helpers
#####################################################


# host = '103.83.15.87'
host =  FTPDetails.objects.get(pk=1).server_address
port = FTPDetails.objects.get(pk=1).portnumber
username = FTPDetails.objects.get(pk=1).username
password = FTPDetails.objects.get(pk=1).password


# Base File
def index(request):
    # print("host",host)
    return render(request, 'base.html')

class possibleSearch(TemplateView):
    # only search movie by Title
    model = UploadMovie
    template_name = 'movies/possible_search.html'

    def get(self, request):
        if request.method == "GET":
            title = request.GET.get('title')

            API = request.GET.get('API')
            link = ""
            cntx = []
            if API == "IMDB":
                #search Movie by making a new connection
                obj = IMDb()
                ia = imdb.IMDb()
                cntx = obj.search_movie(title)
                # for item in cntx:
                #     print(item,item.movieID,item.get('year'))
                link = IMDBAPIDetails.objects.get(pk=1).MoviePageLink
            elif API == "TMDB":
                cntx = get_TMDB_by_Name(title)
                cntx = cntx.results
                link = TMDBAPIDetails.objects.get(pk=1).MoviePageLink
            elif API == "OMDB":
                omdbapikey = OMDBAPIDetails.objects.get(pk=1).API_KEY
                omdb.set_default('apikey',omdbapikey)
                client = omdb.OMDBClient(apikey=omdbapikey)
                movie = omdb.search_movie(title)
                cntx = movie
                link = IMDBAPIDetails.objects.get(pk=1).MoviePageLink

        if cntx:
            return render(request, 'movies/possible_search.html', {'link': link,
                                                                   'context':cntx, 'API':API })
        else:
            return render(request, 'movies/possible_search.html')


#Show movie list + search Movies
class ListViewMovies(ListView):

    context_object_name = 'movieList'
    model = UploadMovie
    template_name = 'movies/search_movies.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['movieList'] = MovieFilter(self.request.GET, queryset=self.get_queryset())
        return context


#Update Movie Information , in case changing the print, poster image get_cast_TMDB_by_ID
@login_required
def UpdateMovie(request):

    all_category = Category.objects.all()
    if request.method == "POST" and request.user.is_authenticated:
        # for x,y in request.POST.items():
        #     print(x,y)

        form = addMovieForm(request.POST, request.FILES)
        ID = request.POST.get('movie_id')
        title = request.POST.get('movie_title')
        year = request.POST.get('year')
        if ID:
            ID = ID.lstrip()
            ID = ID.rstrip()
        else:
            ID = None
        btnpressed = request.POST.get('search')
        print(btnpressed)

        if btnpressed == "Search":
            try:
                if ID is None:
                    print('asdfasdfasdfasdfasd')
                    data = UploadMovie.objects.filter(movie_title__icontains=title)
                    data = data[0]
                    ID = data.movie_id
                # print("asdfas")

                movieInfo = UploadMovie.objects.get( movie_id = ID )

                if movieInfo:
                    form_MODEL = {
                        'movie_title': movieInfo.movie_title,
                        'movie_id': ID,
                        'year': movieInfo.year,
                        'genre': movieInfo.genre,
                        'IMDB_rating': float(movieInfo.IMDB_rating),
                        'writer': movieInfo.writer,
                        'director': movieInfo.director,
                        'cast': movieInfo.cast,
                        'plot': movieInfo.plot,
                        'img' : str(movieInfo.poster_path),
                        'moviecategory': str(movieInfo.category_id),
                        'api': movieInfo.API_name,
                        'destination': movieInfo.destination_location,
                    }
                    messages.success(request,"Desired data is found on the database")

                    jsonmoviedata = json.dumps(form_MODEL)
                    return HttpResponse(jsonmoviedata, content_type="application/json")
            except:
                messages.error(request,"I am sorry, No data Found in the database")
                return render(request, 'movies/update_movie.html', {'form': form, 'cats': all_category, })

        # Convert and Upload Button
        else:
            try:

                ID = request.POST.get('movie_id')
                UploadMovie.objects.filter(movie_id=ID).update(
                    # movie_id = request.POST.get('movie_id'),
                    # category_id = Category.objects.get(category_name = request.POST.get('category')),
                    movie_title = request.POST.get('movie_title'),
                    year = request.POST.get('year'),
                    genre = request.POST.get('genre'),
                    IMDB_rating = request.POST.get('IMDB_rating'),
                    writer = request.POST.get('writer'),
                    director = request.POST.get('director'),
                    cast = request.POST.get('cast'),
                    plot = request.POST.get('plot'),
                    API_name = request.POST.get('API_name'),
                    is_converted = request.POST.get('isConverted'),
                    is_featured = request.POST.get('isFeatured'),
                    destination_location = request.POST.get('destination_location'),
                    poster_path = request.POST.get('poster_path'),
                )

                manual_poster = request.FILES.get('manualImageFile')
                if manual_poster:
                    filename = str(manual_poster)
                    extension = filename.split('.')[1]

                    obj = UploadMovie.objects.get(movie_id=ID)
                    image_path = request.POST.get('destination_location')
                    movie_title = request.POST.get('movie_title')

                    manual_poster_location = image_path + '/poster/' + slugify(movie_title)
                    manual_poster_location = manual_poster_location + '.' + extension

                    with open(manual_poster_location, 'wb+') as destination:
                        for chunk in manual_poster.chunks():
                            destination.write(chunk)

                    UploadMovie.objects.filter(movie_id=ID).update(poster_path=manual_poster_location)

                return HttpResponse("Ok")


                # sample = request.POST.items('poster_path')
                # print(sample)

                # print("Local Path: ", localpath)
                # print("Remote Path: ", remotepath)
                # SFTPTransferGET(filename, localpath, remotepath)
                # SFTPTransferPUT(filename, localpath, remotepath)
                # Convert Handle
                # convert_file_to_mp4(localpath, filename)

            except:

                messages.error(request,"I am sorry, We couldn't complete the update")
                return render(request, 'movies/update_movie.html', {'form': form, 'cats': all_category, })

    else:
        if request.user.is_authenticated:
            form = addMovieForm()  # just pass the form as a context
            return render(request, 'movies/update_movie.html', {'form': form, 'cats': all_category, })
        else:
            return redirect('movies:userlogin')







#Manual Uploading Movie
@login_required
def manualUpload(request):
    all_category = Category.objects.all()
    if request.method == 'POST':

        category_choosen = request.POST.get('category')
        year = request.POST.get('year')
        title = request.POST.get('movie_title')
        ID = request.POST.get('movie_id')
        btnpressed = request.POST.get('btnclicked')

        try:

            if btnpressed == "searchbtn" and year and title :
                destination_locations = Category.objects.get(category_name =category_choosen )
                destination_location = destination_locations.initial_path
                destination_location = destination_location + "/" +  year + "/" + title + " " + year
                location = {
                    'destination' : destination_location,
                }
                jsonmoviedata = json.dumps(location)
                return HttpResponse(jsonmoviedata, content_type="application/json")
            else:
                #first Upload the movie then save the relevent informations ans send response
                destination_location = request.POST.get('destination_location')
                source_location = request.POST.get('source_location')
                category_choosen = request.POST.get('category')

                if destination_location and source_location and category_choosen:
                    #upload the movie to THE FTP.

                    # sample = request.POST.items('poster_path')
                    # print(sample)
                    # print("Local Path: ", localpath)
                    # print("Remote Path: ", remotepath)
                    # SFTPTransferGET(filename, localpath, remotepath)
                    # SFTPTransferPUT(filename, localpath, remotepath)
                    # Convert Handle
                    # convert_file_to_mp4(localpath, filename)


                    #saving Manual movie data set.
                    res = methods.saveMovieInformation(request,category_choosen)
                    if res != "EROR":
                        return HttpResponse('ok')
                    else:
                        messages.error(request, "Couldn't save the manual data. Something wrong with the manual save")
                        return HttpResponseNotFound('error message')
        except:
            return HttpResponseNotFound('error message')

    else:
        form = addMovieForm()
        generateMovieID = methods.generatePrimaryKey()
        return render(request, 'movies/manual_movie_upload.html',{'form':form,'cats': all_category,
                                                                    'movie_id':generateMovieID})


# Add Movie Handle
def addMovies(request):

    # If the user is logged in then let him enter the page
    all_category = Category.objects.all()

    if request.method == 'POST' and request.user.is_authenticated:
        # Search Button
        btnpressed = request.POST.get('btnclicked')

        if btnpressed == "searchbtn":
            form = addMovieForm(request.POST, request.FILES)

            ID = request.POST.get('movie_id')
            ID = ID.lstrip()
            ID = ID.rstrip()
            title = request.POST.get('movie_title')
            title = title.lstrip()
            title = title.rstrip()
            API_choosen = request.POST.get('selectapi')
            category_choosen = request.POST.get('category')
            MOVIE_year = request.POST.get('year')

            # Hit for IMDB with ID
            if len(ID) > 0 and ID.startswith('tt') and API_choosen == 'IMDB':
                IMDB_DATA = methods.get_IMDB_by_ID(ID[2:])

                jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                if jsonmoviedata != "EROR":
                    return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                else:
                    messages.error(request,"Data sending problem to the html")
                    return HttpResponseNotFound("EROR OCCURED")

            elif len(title) > 0 and API_choosen == 'IMDB':
                # find Movie by title
                yearGiven = request.POST.get('year')
                movie_list = methods.get_IMDB_by_Name(title)

                #check if there is any match with year
                for item in movie_list:
                    searched_title = item[1]
                    ID = item[0]
                    print(ID)

                    if yearGiven in searched_title:
                        #Found the movie_TITLE + yearGiven = Matched,There can be multiple, fetching the first one only
                        #Show rest of the list as possible Match
                        ID = item[0]
                        # print(ID)
                    IMDB_DATA = methods.get_IMDB_by_ID(ID) # now fetch information with ID

                    # if IMDB_DATA is not found
                    if IMDB_DATA != "EROR":
                        jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)

                    # if IMDB DATA make json
                    if jsonmoviedata != "EROR":
                        return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")

                #no data found in the list
                return HttpResponseNotFound("No data found with that Name")

            elif API_choosen == 'OMDB' and len(ID) > 0 and ID.startswith("tt"):
                OMDB_APIKEY = OMDBAPIDetails.objects.get(pk=1).API_KEY
                methods.setOMDB_APIKEY(OMDB_APIKEY)
                IMDB_DATA = methods.get_OMDB_by_ID(ID)
                # print(IMDB_DATA)
                jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                if jsonmoviedata != "EROR":
                    return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                else:
                    messages.error(request,"Data sending problem to the html")
                    return HttpResponseNotFound("EROR OCCURED")

            elif len(title) > 0 and API_choosen == 'OMDB':
                # find Movie by title
                yearGiven = request.POST.get('year')
                movie = methods.get_OMDB_by_Name(title)
                if movie == "EROR":
                    movie_list = methods.search_OMDB_by_Name(title)
                    if movie_list == "EROR":
                        return HttpResponseNotFound("EROR OCCURED")

                if yearGiven is not None:
                    # year is given, get movie by title
                    # if not found by title, search for movie list
                    # if not found by movie list , not found

                    if yearGiven in movie['year']:
                        ID = movie['imdb_id']
                        IMDB_DATA = movie
                        jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                        # print(IMDB_DATA)
                        if jsonmoviedata != "EROR":
                            return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                    else:
                        movie_list = methods.search_OMDB_by_Name(title)
                        for item in movie_list:
                            if yearGiven in item['year']:
                                ID = item['imdb_id']
                                IMDB_DATA = item
                                jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                                if jsonmoviedata != "EROR":
                                    return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                        return HttpResponseNotFound("Movie Not found")

                else:
                    # year is not given , search for movie list and show the first one from the movie_list
                    movie_list = methods.search_OMDB_by_Name(title)
                    IMDB_DATA = movie
                    ID = movie['imdb_id']
                    jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                    if jsonmoviedata != "EROR":
                        return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                    else:
                        return HttpResponseNotFound("Movie Not found")

                # else:
                #     return HttpResponseNotFound("EROR OCCURED DURING FIRST FETCH OF IMDB")

                return HttpResponse("OK")

            elif API_choosen == 'TMDB' and len(ID) > 0:
                TMDB_APIKEY = TMDBAPIDetails.objects.get(pk=1).API_KEY
                methods.setTMDB_APIKEY(TMDB_APIKEY) #setting TMDB API KEY to methods.py

                TMDB_DATA = methods.get_TMDB_by_ID(ID)
                if TMDB_DATA != "EROR":
                    jsonmoviedata = methods.flyTheInformation(request,TMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                else:

                    return HttpResponseNotFound("EROR OCCURED DURING FIRST FETCH OF TMDB")

                if jsonmoviedata != "EROR":
                    return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                else:
                    messages.error(request,"Data sending problem to the html")
                    return HttpResponseNotFound("EROR OCCURED")

            elif len(title) > 0 and API_choosen == 'TMDB':

                # find Movie by title
                yearGiven = request.POST.get('year')
                movie_list = methods.get_TMDB_by_Name(title)

                if movie_list != "EROR":
                    #check if there is any match with year
                    # print("res" , movie_list.results[0])
                    searched_title = movie_list.results[0]['title']
                    ID = movie_list.results[0]['id']

                    for s in movie_list.results:
                        if yearGiven in s['release_date']:
                            searched_title = s['title']
                            ID = s['id']
                    TMDB_DATA = methods.get_TMDB_by_ID(ID) # now fetch information with ID
                    # if TMDB_DATA is not found
                    if TMDB_DATA != "EROR":
                        jsonmoviedata = methods.flyTheInformation(request,TMDB_DATA,ID,API_choosen,category_choosen,MOVIE_year)
                    else:
                        return HttpResponseNotFound("EROR OCCURED DURING FIRST FETCH OF IMDB")

                    # if TMDB_DATA couldn't make json
                    if jsonmoviedata != "EROR":
                        return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                    else:
                        messages.error(request,"Data sending problem to the html")
                        return HttpResponseNotFound("EROR OCCURED")

                    # return HttpResponse("OK")
                else:
                    return HttpResponseNotFound("EROR")
                pass
            elif len(ID) == 0 and len(MOVIE_title) > 0 and len(MOVIE_year) > 0:
                possible_DATA = methods.get_IMDB_by_Name(MOVIE_title)
                # print(possible_DATA)
                return render(request, 'movies/add_movies.html', {'form': form, 'cats': all_category, })

        # Convert and Upload Button
        else:
            #get remotepath form database model SECTION
            localpath = request.POST.get('source_location')
            remotepath = '/mnt/Games/Avengers/'
            category_choosen = request.POST.get('category')

            filename = request.POST.get('filename')
            # print(filename)
            # sample = request.POST.items('poster_path')
            # print(sample)
            # print("Local Path: ", localpath)
            # print("Remote Path: ", remotepath)

            # SFTPTransferGET(filename, localpath, remotepath)
            # status = methods.SFTPTransferPUT(filename, localpath, remotepath)
            # convert_file_to_mp4(localpath, filename)
            # Convert Handle
            # print(status)
            status = "OK"
            if status == "OK":
                if methods.saveMovieInformation(request,category_choosen) == True:
                    dict = {'TEST':'ASDF'}
                    jsonmoviedata = json.dumps(dict)
                    return HttpResponse(jsonmoviedata, content_type="application/json")
                else:
                    # print("movie transferred but couldn't save the information")
                    return HttpResponseNotFound("Couldn't save the movie information")
            else:
                #print("coundn't SUCCESFULLY transfer the movie")
                return HttpResponseNotFound("Couldn't Transfer the movie")



    else:
        if request.user.is_authenticated:
            form = addMovieForm()  # just pass the form as a context
            return render(request, 'movies/add_movies.html', {'form': form, 'cats': all_category, })
        else:
            return redirect('movies:userlogin')
