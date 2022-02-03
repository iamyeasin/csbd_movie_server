from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse,JsonResponse,HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
from imdb import IMDb, helpers
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from . models import Category,UploadMovie
from settings.models import *
from movies import models
from . forms import *
import paramiko
import sys,re,os,json,requests
from django.core import serializers
import datetime
from time import gmtime, strftime
import tmdbsimple as tmdb
import omdb
from django.template.defaultfilters import slugify
##############################################################

### Add / Update / Manual add Movie Method section

########################### START ACCOUNT AUTHENTICATION SECTION ####################
host =  FTPDetails.objects.get(pk=1).server_address
port = FTPDetails.objects.get(pk=1).portnumber
username = FTPDetails.objects.get(pk=1).username
password = FTPDetails.objects.get(pk=1).password


# User Login for Moderators or Admins only
def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # make authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:  # Found Login Credentials in Database
            login(request, user)
            messages.success(request, 'Login Successfull')
            return HttpResponseRedirect(reverse('movies:addmovies'), {'user': user})
        else:
            messages.error(request, 'Do I know you? I have no record of your Identity')
            return HttpResponseRedirect(reverse('movies:userlogin'), {'user': user})
    else:
        return render(request, 'accounts/user_login.html')



# Add Movies but requires login authentication
@login_required
def userLogout(request):
    logout(request)
    request.session.flush()
    return redirect('movies:userlogin')


########################### END ACCOUNT AUTHENTICATION SECTION ####################



########################### START IMDB FETCH SECTION ####################

# Get IMDb info by ID
def get_IMDB_by_ID(getimdbid):
    try:
        movie = None
        obj = IMDb('http')
        movie = obj.get_movie(getimdbid)  # get movie info
        return movie

    except IMDbError as e:
        messages.error("Having problem to fetch INFORMATION FROM IMDB",e)
        return "EROR"



# Search IMDb info by Name and Year
def get_IMDB_by_Name(name):
    try:
        searched_movie_dict = []
        obj = IMDb()
        search_result = obj.search_movie(name)
        for item in search_result:
            sample = []
            sample.append(item.movieID)
            sample.append(item['smart long imdb canonical title'])
            title = item['smart long imdb canonical title']
            if "(TV)" not in title: #Don't need to search on the TV series
                searched_movie_dict.append(sample)

        return searched_movie_dict
    except IMDbError as e:
        messages.error("PROBLEM FOUND DURING FETCHING IMDB MOVIE BY TITLE",e)
        return "EROR"




########################### END IMDB FETCH SECTION ####################



########################### START TMDB FETCH SECTION ####################

TMDB_APIKEY = TMDBAPIDetails.objects.get(pk=1).API_KEY # set programatically apikey

def setTMDB_APIKEY(key):
    TMDB_APIKEY = key

def getTMDB_APIKEY():
    return TMDB_APIKEY


# Get TMDB info by ID
def get_TMDB_by_ID(gettmdbid):
    # print(getTMDB_APIKEY())
    try:
        tmdb.API_KEY =  getTMDB_APIKEY()
        # get movie info
        getMovie = tmdb.Movies(gettmdbid) # search movie by ID
        movie = getMovie.info()
        return movie

    except:
        # messages.error("Having problem to fetch INFORMATION FROM TMDB")
        # print(tmdb.errors.APIKeyError)
        return "EROR"


def get_cast_TMDB_by_ID(ID):
    try:
        tmdb.API_KEY =  getTMDB_APIKEY()
        getMovie = tmdb.Movies(ID)
        response = getMovie.credits()
        casts = response['cast']
        cast = []
        for c in casts:
            cast.append(c['name'])

        return cast
    except:
        return "EROR"


def get_director_TMDB_by_ID(ID):
    try:
        tmdb.API_KEY =  getTMDB_APIKEY()
        getMovie = tmdb.Movies(ID)
        response = getMovie.credits()
        crew = response['crew']
        director = []

        for c in crew:
            jb = c['job'] # crew job
            if jb == "Director":
                director.append(c['name'])

        # print("DASdfasdfaasdfasdfasdfasdfassd ",director)

        return director
    except:
        return "EROR"


def get_writer_TMDB_by_ID(ID):
    try:

        tmdb.API_KEY =  getTMDB_APIKEY() #defined at the top of the page
        getMovie = tmdb.Movies(ID)
        response= getMovie.credits()
        crew = response['crew']
        writers = []

        for c in crew:
            dept = c['department'] # writer is in crew depertment
            if dept == 'Writing':
                writers.append(c['name'])

        return writers
    except:
        return "EROR"




# Search TMDb info by Name and Year
def get_TMDB_by_Name(title):
    try:
        # print(title,TMDB_APIKEY)
        searched_movie_dict = []
        tmdb.API_KEY = TMDB_APIKEY
        search = tmdb.Search()
        response = search.movie(query=title)
        # print(response[0])
        return search

    except :
        return "EROR"


########################### END TMDB FETCH SECTION ####################





########################### START OMDB FETCH SECTION ####################

OMDB_APIKEY = OMDBAPIDetails.objects.get(pk=1).API_KEY # set programatically apikey

def setOMDB_APIKEY(key):
    OMDB_APIKEY = key

def getOMDB_APIKEY():
    return OMDB_APIKEY


# Get TMDB info by ID
def get_OMDB_by_ID(getimdbid):
    # print(getTMDB_APIKEY())
    # OMDB has no own database, It fethes Data from IMDB
    try:
        # print(OMDB_APIKEY,getimdbid)
        omdb.set_default('apikey',OMDB_APIKEY)
        client = omdb.OMDBClient(apikey=OMDB_APIKEY)
        # get movie info
        movie = omdb.imdbid(getimdbid) # search movie by ID
        return movie

    except:
        # messages.error("Having problem to fetch INFORMATION FROM TMDB")
        # print(tmdb.errors.APIKeyError)
        return "EROR"



# Search TMDb info by Name and Year
def get_OMDB_by_Name(title):
    try:
        # print(title,TMDB_APIKEY)
        omdb.set_default('apikey',OMDB_APIKEY)
        client = omdb.OMDBClient(apikey=OMDB_APIKEY)
        movie = omdb.title(title)
        # print(response[0])
        return movie
    except :
        return "EROR"

def search_OMDB_by_Name(title):
    try:
        # print(title,TMDB_APIKEY)
        omdb.set_default('apikey',OMDB_APIKEY)
        client = omdb.OMDBClient(apikey=OMDB_APIKEY)
        movie = omdb.search(title)
        # print(response[0])
        return movie

    except :
        return "EROR"


########################### END OMDB FETCH SECTION ####################



########################### START SFTP SECTION ####################


def mkdir_p(sftp, remote_directory):

    print("vai dukhsen")
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return

    try:
        sftp.chdir(remote_directory) # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        print(basename)
        mkdir_p(sftp, dirname) # make parent directories
        sftp.mkdir(basename) # sub-directory missing, so created it
        sftp.chdir(basename)
        return True



def deleteAFile(filepath):

    try:
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.load_system_host_keys()
        #SFTP host,port,user,password,
        sshClient.connect(FTPDetails.objects.get(pk=1).server_address, FTPDetails.objects.get(pk=1).portnumber, username=FTPDetails.objects.get(pk=1).username, password=FTPDetails.objects.get(pk=1).password)
        sftp = sshClient.open_sftp()

        sftp.remove(filepath)
        return "OK"

    except:
        return "EROR"


# SFTP Transfer PUT File to Server
def SFTPTransferPUT(filename, localpath, remotepath):

    try:
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.load_system_host_keys()
        print("Yeasin")
        sshClient.connect(host, port, username, password)
        print("Nirob")
        sshClient.exec_command('mkdir -p ' + remotepath)

        print("LocalPath -> ",localpath,"RemotePath -> ", remotepath)
        sftp = sshClient.open_sftp()
        localpath = os.path.join(localpath, filename)

        try:
            sftp.chdir(remotepath)
        except IOError:
            mkdir_p(sftp, remotepath)
            sftp.chdir(remotepath)

        remotepath = os.path.join(remotepath, filename)
        print(remotepath)
        sftp.put(localpath, remotepath)
        sftp.close()
        return "OK"
    except:
        return "EROR"



# SFTP Transfer GET file from Server
def SFTPTransferGET(filename, localpath, remotepath):

    try:
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.load_system_host_keys()
        sshClient.connect(host, port, username, password)
        sshClient.exec_command('mkdir -p ' + remotepath)
        sftp = sshClient.open_sftp()

        localpath = os.path.join(localpath, filename)

        try:
            sftp.chdir(remotepath)
        except IOError:
            mkdir_p(sftp, remotepath)
            sftp.chdir(remotepath)

        remotepath = os.path.join(remotepath, filename)
        sftp.get(remotepath, localpath)
        sftp.close()
        # messages.success(request,"DATA IS ON THE FTP SERVER")
        return "OK"
    except:
        # messages.error(request,"COULDN'T GET THE DATA ON THE FTP SERVER")
        return "EROR"




########################### END SFTP SECTION ####################



########################### FILE CONVERT SECTION ####################


# Convert File to MP4
def convert_file_to_mp4(source_location, filename):
    try:
        # Input Path
        vid_input = os.path.join(source_location, filename)
        # Removing Extension and add MP4 Extension
        filename = filename.split('.')[0] + ".mp4"

        # Converted Path
        vid_output = os.path.join(source_location, filename)
        os.system("ffmpeg -i " + vid_input + " -vcodec copy -acodec copy -strict experimental " + vid_output)
        # messages.success(request,"MOVIE CONVERTED SUCCESFULLY")
        return "OK"
    except:
        # messages.error(request,"COULDN'T CONVERT THE MOVIE")
        return "ERROR"



########################### FILE CONVERT SECTION ####################


########################### RAW METHODS SECTION ####################

def cleanDirectorData(IMDB_DATA):
    MOVIE_DIRECTOR = []
    try:
        for dr in IMDB_DATA['director']:
            a = dr['name']
            a = a.replace('"', '')
            a = a.replace('[', '')
            a = a.replace(']', '')
            MOVIE_DIRECTOR.append(a)
    except:
        MOVIE_DIRECTOR = ""

    return MOVIE_DIRECTOR


def cleanWriterData(IMDB_DATA):
    MOVIE_WRITER = []
    try:
        for wr in IMDB_DATA['writer']:
            a = wr['name']
            a = a.replace('"', '')
            a = a.replace('[', '')
            a = a.replace(']', '')
            MOVIE_WRITER.append(a)
    except:
        MOVIE_WRITER = ""
    return MOVIE_WRITER

def cleanCastData(IMDB_DATA):
    MOVIE_CAST = []
    try:
        for ct in IMDB_DATA['cast']:
            a = ct['name']
            a = a.replace('[', '')
            a = a.replace(']', '')
            a = a.replace('"', '')
            MOVIE_CAST.append(a)
    except:
        MOVIE_CAST = ""
    return MOVIE_CAST



def saveMovieInformation(request,category_choosen ):

    url = request.POST.get('poster_path')
    if url.startswith('http'):

        try:
        # if (1):
            filename = request.POST.get('filename')
            # manualImage = request.FILES.get('manualImageFile') # Manual poster
            movie_ID = request.POST.get('movie_id')
            cat_ID = Category.objects.get(category_name=category_choosen)
            movie_TITLE = request.POST.get('movie_title')
            YEAR = request.POST.get('year')
            GENRE = request.POST.get('genre')
            IMDB_RATING = request.POST.get('IMDB_rating')
            WRITER = request.POST.get('writer')
            DIRECTOR = request.POST.get('director')
            CAST = request.POST.get('cast')
            PLOT = request.POST.get('plot')
            API_NAME = request.POST.get('API_name')
            IS_CONVERTED = request.POST.get('isConverted')
            IS_FEATURED = request.POST.get('isFeatured')
            DESTINATION_LOCATION = request.POST.get('destination_location')
            filePath = os.path.join(DESTINATION_LOCATION, filename)

            # print(filename,movie_ID,cat_ID,slugify(movie_TITLE),YEAR,GENRE,IMDB_RATING,WRITER,DIRECTOR,CAST,PLOT,API_NAME,IS_CONVERTED,IS_FEATURED,DESTINATION_LOCATION,filePath )
            # print("sadf")
            uploadInfo = UploadMovie(
                movie_id = movie_ID,
                category_id = cat_ID,
                movie_title = (movie_TITLE),
                year = YEAR ,
                genre = GENRE,
                IMDB_rating = IMDB_RATING ,
                writer = WRITER ,
                director = DIRECTOR,
                cast = CAST,
                plot = PLOT,
                API_name = API_NAME,
                is_converted = IS_CONVERTED,
                is_featured = IS_FEATURED,
                destination_location = DESTINATION_LOCATION,
                # file_path = filePath,
            )

            uploadInfo.save()

            # uploadInfo.save()

            # Section: Grab Poster
            url = request.POST.get('poster_path')
            image_url = url
            try:
                # print(image_url)
                img_temp = NamedTemporaryFile()
                img_temp.write(urlopen(image_url).read())
            except:
                messages.error(request,"COULDN'T WRITE THE TEMPORARY IMAGE FILE")

            # print(request.POST.get('new_poster_path'))
            # Location Join and rename poster
            # var = os.path.join(request.POST.get('movie_title'))
            # print(var)
            # uploadInfo.poster_path.save((var + '.jpg'), File(img_temp))
            # print("Bal")
            path = os.path.join(movie_TITLE)
            # print("bal amar")
            img_data = requests.get(image_url).content
            posterlocation = DESTINATION_LOCATION + "/poster"
            npath = posterlocation + "/" + movie_ID + "_" + slugify(movie_TITLE) + '.jpg'

            if not os.path.exists( posterlocation ):
               os.makedirs( posterlocation )

            with open( npath, 'wb') as handler:
                handler.write( img_data )

            uploadInfo.poster_path = npath
            uploadInfo.save()
            img_temp.flush()
            messages.success(request, 'Your Data is saved Successfully!')
            return True
        except:
            return False
    else:
        # save Manual Data

        try:
            manualImage = request.FILES.get('manualImageFile') # Manual poster
            filename = request.POST.get('filename')
            movie_ID = request.POST.get('movie_id')
            cat_ID = Category.objects.get(category_name=category_choosen)
            movie_TITLE = request.POST.get('movie_title')
            YEAR = request.POST.get('year')
            GENRE = request.POST.get('genre')
            IMDB_RATING = request.POST.get('IMDB_rating')
            WRITER = request.POST.get('writer')
            DIRECTOR = request.POST.get('director')
            CAST = request.POST.get('cast')
            PLOT = request.POST.get('plot')
            API_NAME = request.POST.get('API_name')
            IS_CONVERTED = request.POST.get('isConverted')
            IS_FEATURED = request.POST.get('isFeatured')
            DESTINATION_LOCATION = request.POST.get('destination_location')
            filePath = os.path.join(DESTINATION_LOCATION, filename)

            if manualImage is not None:

                uploadInfo = UploadMovie(
                    movie_id = movie_ID,
                    category_id = cat_ID,
                    movie_title = movie_TITLE,
                    year = YEAR ,
                    genre = GENRE,
                    IMDB_rating = IMDB_RATING ,
                    writer = WRITER ,
                    director = DIRECTOR,
                    cast = CAST  ,
                    plot = PLOT,
                    API_name = API_NAME,
                    is_converted = IS_CONVERTED,
                    is_featured = IS_FEATURED,
                    destination_location = DESTINATION_LOCATION,
                    poster_path=manualImage,
                    file_path = filePath,
                )

                uploadInfo.save()
                # print("MOVIE SAVED")

                messages.success(request, 'Your Data is saved Successfully!')
                return "Saved"
            else:
                messages.error(request, "Couldn't save the manual data. Something wrong with the manual save")
                return "EROR"
        except:
            return "EROR"
            messages.error(request, "Couldn't save the manual data. Something wrong with the manual save")





############### SEND FETECHED MOVIE INFORMATION TO THE HTML PAGE #####

def flyTheInformation(request,DATA,ID,API_choosen,category_choosen,MOVIE_year):

    if DATA and API_choosen == 'IMDB':
        IMDB_DATA = DATA
        # list for director , writer, casts
        if API_choosen == "OMDB" and  (not ID.startswith("tt")):
            ID = "tt" + ID


        MOVIE_year = str(IMDB_DATA['year'])
        MOVIE_DIRECTOR = cleanDirectorData(IMDB_DATA)
        MOVIE_WRITER = cleanWriterData(IMDB_DATA)
        MOVIE_CAST = cleanCastData(IMDB_DATA)

        try:
            MOVIE_title = IMDB_DATA['title']
        except:
            MOVIE_title = "NOT_FOUND"

        try:
            MOVIE_poster = IMDB_DATA['full-size cover url']
        except:
            MOVIE_poster = ""

        try:
            MOVIE_plot = IMDB_DATA['plot']
        except:
            MMOVIE_plot = "NOT_FOUND"

        MOVIE_plot = MOVIE_plot[:400]

        # Destination Location get from database and join the path
        temp = category_choosen
        MOVIE_category = category_choosen
        destination_location = Category.objects.get(category_name = category_choosen)

        destination_location = destination_location.initial_path
        try:
            MOVIE_year = str(IMDB_DATA['year'])
        except:
            MOVIE_year = "1800"

        try:
            GENRE = IMDB_DATA['genre']
        except:
            GENRE = "NOT_FOUND"

        try:
            RATING = IMDB_DATA['rating']
        except:
            RATING = 0.0

        destination_location = destination_location + "/" +  MOVIE_year + "/" + MOVIE_title + " " + MOVIE_year
        # Build json Data
        form_IMDB = {
            'movie_title': MOVIE_title,
            'movie_id': ID,
            'year': MOVIE_year,
            'genre': GENRE,
            'IMDB_rating': RATING,
            'writer': MOVIE_WRITER,
            'director': MOVIE_DIRECTOR,
            'cast': MOVIE_CAST,
            'plot': MOVIE_plot,
            'img' : MOVIE_poster,
            'moviecategory': category_choosen,
            'api': API_choosen,
            'destination': destination_location,
        }
        return form_IMDB

    elif API_choosen == "TMDB" and DATA:
        TMDB_DATA = DATA
        # print(TMDB_DATA)
        # send TMDB information to the user

        try:
            datestr = TMDB_DATA['release_date']
            year = datestr.split('-',1) # Spliting the date into year -> 2018-01-28
            MOVIE_year = year[0]
        except:
            MOVIE_year = "1800"


        MOVIE_DIRECTOR = get_director_TMDB_by_ID(ID)
        MOVIE_WRITER = get_writer_TMDB_by_ID(ID)
        MOVIE_CAST = get_cast_TMDB_by_ID(ID)
        # print(MOVIE_year,MOVIE_CAST,MOVIE_WRITER,MOVIE_DIRECTOR)

        if MOVIE_DIRECTOR == "EROR" or MOVIE_WRITER == "EROR" or MOVIE_CAST == "EROR":
            return "EROR"

        try:
            MOVIE_title = TMDB_DATA['title']
        except:
            MOVIE_title = "NOT_FOUND"

        try:
            #Example -> https://image.tmdb.org/t/p/w500/v3QyboWRoA4O9RbcsqH8tJMe8EB.jpg
            baseURL = "https://image.tmdb.org/t/p/w500" # got it from API docs , for specific size image
            foundPath = TMDB_DATA['poster_path'] # the image link
            MOVIE_poster = baseURL+foundPath # building image link
        except:
            MOVIE_poster = ""

        try:
            MOVIE_plot = TMDB_DATA['overview']
        except:
            MOVIE_plot = "NOT_FOUND"


        MOVIE_plot = MOVIE_plot[:400]

        # Destination Location get from database and join the path
        temp = category_choosen
        MOVIE_category = category_choosen
        destination_location = Category.objects.get(category_name = category_choosen)
        destination_location = destination_location.initial_path

        try:
            GENRE = []
            gen = TMDB_DATA['genres']
            for g in gen:
                GENRE.append(g['name'])
        except:
            GENRE = "NOT_FOUND"

        try:
            RATING = TMDB_DATA['vote_average']
        except:
            RATING = 0.0

        # print("Poster",MOVIE_year)

        destination_location = destination_location + "/" +  MOVIE_year + "/" + MOVIE_title + " " + MOVIE_year
        # Build json Data
        form_TMDB = {
            'movie_title': MOVIE_title,
            'movie_id': ID,
            'year': MOVIE_year,
            'genre': GENRE,
            'IMDB_rating': RATING,
            'writer': MOVIE_WRITER,
            'director': MOVIE_DIRECTOR,
            'cast': MOVIE_CAST,
            'plot': MOVIE_plot,
            'img' : MOVIE_poster,
            'moviecategory': category_choosen,
            'api': API_choosen,
            'destination': destination_location,
        }
        # print("TESTSTDFDDF ->" , form_TMDB)
        return form_TMDB

    elif DATA and API_choosen == 'OMDB' :
        #OMDB has only IMDB dataset
        IMDB_DATA = DATA
        # list for director , writer, casts
        if API_choosen == "IMDB" and  not API_choosen.startswith("tt"):
            ID = "tt" + ID

        try:
            MOVIE_DIRECTOR = IMDB_DATA['director']
        except:
            MOVIE_DIRECTOR = "NOT_FOUND"

        try:
            MOVIE_WRITER = IMDB_DATA['writer']
        except:
            MOVIE_WRITER = "NOT_FOUND"

        try:
            MOVIE_CAST = IMDB_DATA['actors']
        except:
            MOVIE_CAST = "NOT_FOUND"

        try:
            MOVIE_title = IMDB_DATA['title']
        except:
            MOVIE_title = "NOT_FOUND"

        try:
            MOVIE_poster = IMDB_DATA['poster']
        except:
            MOVIE_poster = ""

        MOVIE_plot = "NOT_FOUND"
        try:
            MOVIE_plot = IMDB_DATA['plot']
        except:
            MMOVIE_plot = "NOT_FOUND"

        MOVIE_plot = MOVIE_plot[:400]

        # Destination Location get from database and join the path
        temp = category_choosen
        MOVIE_category = category_choosen
        destination_location = Category.objects.get(category_name = category_choosen)

        destination_location = destination_location.initial_path
        try:
            MOVIE_year = str(IMDB_DATA['year'])
        except:
            MOVIE_year = "1800"

        try:
            GENRE = IMDB_DATA['genre']
        except:
            GENRE = "NOT_FOUND"

        try:
            RATING = IMDB_DATA['imdb_rating']
        except:
            RATING = 0.0

        destination_location = destination_location + "/" +  MOVIE_year + "/" + MOVIE_title + " " + MOVIE_year
        # Build json Data
        form_IMDB = {
            'movie_title': MOVIE_title,
            'movie_id': ID,
            'year': MOVIE_year,
            'genre': GENRE,
            'IMDB_rating': RATING,
            'writer': MOVIE_WRITER,
            'director': MOVIE_DIRECTOR,
            'cast': MOVIE_CAST,
            'plot': MOVIE_plot,
            'img' : MOVIE_poster,
            'moviecategory': category_choosen,
            'api': API_choosen,
            'destination': destination_location,
        }
        return form_IMDB
    else:
        return "EROR"









################## GENERATE MANUAL PRIMARY KEY ##############

def generatePrimaryKey():
    # newMovieID = MID#CurrentDate + currentTime
    currentTime = strftime("%Y%m%d%H%M%S",gmtime())
    key= "MID#" + currentTime

    idExists = UploadMovie.objects.filter(movie_id=key).count()
    if idExists == 0:
        return key
    else:
        while idExists == 0:
            currentTime = strftime("%Y%m%d%H%M%S",gmtime())
            key = "MID#" + currentTime
            idExists = UploadMovie.objects.filter(movie_id=key).count()

            return key
