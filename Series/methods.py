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
from settings.models import *
from . models import *
from . forms import *
import paramiko,sys,os,re,json
from django.core import serializers
import datetime,omdb,movies
from time import gmtime, strftime
import tmdbsimple as tmdb
import tvdbsimple as tvdb
from django.db.models import Q
import requests
from deletemovie import models


##############################################################



host =  FTPDetails.objects.get(pk=1).server_address
port = FTPDetails.objects.get(pk=1).portnumber
username = FTPDetails.objects.get(pk=1).username
password = FTPDetails.objects.get(pk=1).password



######################## DELTE EPISODE FROM FTP #######################

def SFTP_deleteEpisode( filepath ):

    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.load_system_host_keys()
    # print("asdfasd"host,port,username,password)
    sshClient.connect(host, port, username, password)
    sftp = sshClient.open_sftp()

    # removing the episode file
    try:
        sftp.remove(filepath)
        return "OK"
    except:
        return "EROR"


######################## end DELTE EPISODE FROM FTP #######################


########################## START TMDB FETCH SECTION #####################


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
        getTv = tmdb.TV(gettmdbid) # search tv by ID
        tv = getTv.info()
        return tv

    except:
        # messages.error("Having problem to fetch INFORMATION FROM TMDB")
        # print(tmdb.errors.APIKeyError)
        return "EROR"


def get_cast_TMDB_by_ID(ID):
    try:
        tmdb.API_KEY =  getTMDB_APIKEY()
        getTv = tmdb.TV(ID)
        response = getTv.credits()
        casts = response['cast']
        cast = []
        for c in casts:
            cast.append(c['name'])

        return cast
    except:
        return "EROR"


def get_writer_TMDB_by_ID(ID):
    try:

        tmdb.API_KEY =  getTMDB_APIKEY() #defined at the top of the page

        getTv = tmdb.TV(ID)
        response= getTv.credits()
        # print(ID,getTv)
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




######################### END TMDB FETCH SECTION #######################



########################## START TVDB FETCH SECTION #####################

# TVDB_APIKEY = 'Z5SC1ZD07NNS8TDC' #default API KEY
TVDB_APIKEY = TMDBAPIDetails.objects.get(pk=2).API_KEY # set programatically apikey

def setTVDB_APIKEY(key):
    TVDB_APIKEY = key

def getTVDB_APIKEY():
    return TVDB_APIKEY


# # Get TVDB info by ID
def get_TVDB_by_ID(gettmdbid):
    # print(getTMDB_APIKEY())
    try:
        tvdb.KEYS.API_KEY =  getTVDB_APIKEY()
        # get movie info
        show = tvdb.Series(gettmdbid) # search tv by ID
        tv = show.info()
        return tv

    except:
        # messages.error("Having problem to fetch INFORMATION FROM TMDB")
        # print(tmdb.errors.APIKeyError)
        return "EROR"

#
# def get_cast_TMDB_by_ID(ID):
#     try:
#         tmdb.API_KEY =  getTMDB_APIKEY()
#         getTv = tmdb.TV(ID)
#         response = getTv.credits()
#         casts = response['cast']
#         cast = []
#         for c in casts:
#             cast.append(c['name'])
#
#         return cast
#     except:
#         return "EROR"
#
#
# def get_writer_TMDB_by_ID(ID):
#     try:
#
#         tmdb.API_KEY =  getTMDB_APIKEY() #defined at the top of the page
#
#         getTv = tmdb.TV(ID)
#         response= getTv.credits()
#         # print(ID,getTv)
#         crew = response['crew']
#         writers = []
#
#         for c in crew:
#             dept = c['department'] # writer is in crew depertment
#             if dept == 'Writing':
#                 writers.append(c['name'])
#
#         return writers
#     except:
#         return "EROR"
#
#
#
#
# # Search TMDb info by title
def get_TMDB_by_Name(title):
    try:
        # print(title,TMDB_APIKEY)
        searched_movie_dict = []
        tmdb.API_KEY = TMDB_APIKEY
        search = tmdb.Search()
        response = search.tv(query=title)
        # print(response[0])
        return search

    except :
        return "EROR"




######################### END TVDB FETCH SECTION #######################



########################## START IMDB FETCH SECTION ####################

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
            #Don't need to search on the TV series
            searched_movie_dict.append(sample)

        return searched_movie_dict
    except IMDbError as e:
        messages.error("PROBLEM FOUND DURING FETCHING IMDB MOVIE BY TITLE",e)
        return "EROR"




########################### END IMDB FETCH SECTION ####################


############### SEND FETECHED MOVIE INFORMATION TO THE HTML PAGE #####

def flyTheInformation(request,DATA,ID,API_choosen,category_choosen,MOVIE_year):

    if DATA and API_choosen == 'IMDB':
        IMDB_DATA = DATA
        # list for director , writer, casts
        if not (ID.startswith("tt")):
            ID = "tt" + ID

        year = str(IMDB_DATA['year'])
        TV_WRITER = movies.methods.cleanWriterData(IMDB_DATA)
        TV_CAST = movies.methods.cleanCastData(IMDB_DATA)

        try:
            TV_title = IMDB_DATA['title']
        except:
            TV_title = "NOT_FOUND"

        try:
            TV_poster = IMDB_DATA['full-size cover url']
        except:
            TV_poster = ""

        try:
            TV_plot = IMDB_DATA['plot']
        except:
            TV_plot = "NOT_FOUND"

        TV_plot = TV_plot[:400]

        # Destination Location get from database and join the path
        # provide full path where tv series will be saved
        temp = category_choosen
        MOVIE_category = category_choosen
        destination_location = CategoryForTv.objects.get(category_name = category_choosen)
        destination_location = destination_location.initial_path

        try:
            TV_year = str(IMDB_DATA['year'])
        except:
            TV_year = "1800"

        try:
            GENRE = IMDB_DATA['genre']
        except:
            GENRE = "NOT_FOUND"

        try:
            RATING = IMDB_DATA['rating']
        except:
            RATING = 0.0

        destination_location = destination_location + "/" +  TV_year + "/" + slugify(TV_title) + " " + TV_year

        NOS = 0 # Number of seasons
        try:
            NOS = IMDB_DATA['number of seasons']
        except:
            NOS = 0

        seriesYears = year
        try:
            seriesYears = IMDB_DATA['series years']
        except:
            seriesYears = year

        # if( not (int(RATING) in range(0,11)) ):
        #     RATING = 0.0

        # Build json Data
        form_IMDB = {
            'TV_title': TV_title,
            'TV_id': ID,
            'year': year,
            'genre': GENRE,
            'rating': RATING,
            'writer': TV_WRITER,
            'noOfSeason': NOS,
            'seriesYear': seriesYears,
            'cast': TV_CAST,
            'plot': TV_plot,
            'img' : TV_poster,
            'tvcategory': category_choosen,
            'api': API_choosen,
            'destination': destination_location,
        }
        return form_IMDB

    elif API_choosen == "TMDB" and DATA:
        TMDB_DATA = DATA
        # print(TMDB_DATA)
        # send TMDB information to the user

        try:
            datestr = TMDB_DATA['first_air_date']
            year = datestr.split('-',1) # Spliting the date into year -> 2018-01-28
            year = year[0]
        except:
            year = "1800"

        try:
            datestr = TMDB_DATA['last_air_date']
            years = datestr.split('-',1) # Spliting the date into year -> 2018-01-28
            seriesYears = years[0]
        except:
            seriesYears = year

        TV_WRITER = get_writer_TMDB_by_ID(ID)
        TV_CAST = get_cast_TMDB_by_ID(ID)
        # print(year,TV_CAST,TV_WRITER)

        if TV_WRITER == "EROR" or TV_CAST == "EROR":
            return "EROR"

        try:
            TV_title = TMDB_DATA['name']
        except:
            TV_title = "NOT_FOUND"

        try:
            #Example -> https://image.tmdb.org/t/p/w500/v3QyboWRoA4O9RbcsqH8tJMe8EB.jpg
            baseURL = "https://image.tmdb.org/t/p/w500" # got it from API docs , for specific size image
            foundPath = TMDB_DATA['poster_path'] # the image link
            TV_poster = baseURL+foundPath # building image link
        except:
            TV_poster = ""

        try:
            TV_plot = TMDB_DATA['overview']
        except:
            TV_plot = "NOT_FOUND"


        TV_plot = TV_plot[:400]

        # Destination Location get from database and join the path
        temp = category_choosen
        TV_category = category_choosen
        destination_location = CategoryForTv.objects.get(category_name = category_choosen)
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
        NOS = 0 # Number of seasons
        try:
            NOS = TMDB_DATA['number_of_seasons']
        except:
            NOS = 0

        destination_location = destination_location + "/" +  str(year) + "/" + slugify(TV_title) + " " + str(year)
        # Build json Data
        # print(TV_WRITER)
        # if( not (int(RATING) in range(0,11)) ):
        #     RATING = 0.0

        form_TMDB = {
            'TV_title': TV_title,
            'TV_id': ID,
            'year': year,
            'genre': GENRE,
            'rating': RATING,
            'writer': TV_WRITER,
            'noOfSeason': NOS,
            'seriesYear': seriesYears,
            'cast': TV_CAST,
            'plot': TV_plot,
            'img' : TV_poster,
            'moviecategory': category_choosen,
            'api': API_choosen,
            'destination': destination_location,
        }
        # print("TESTSTDFDDF ->" , form_TMDB)
        return form_TMDB

    elif DATA and API_choosen == 'TVDB' :
        TVDB_DATA = DATA
        # list for director , writer, casts

        TV_DIRECTOR = "NOT_FOUND"
        TV_WRITER = "NOT_FOUND"
        TV_CAST = "NOT_FOUND"

        try:
            TV_title = TVDB_DATA['seriesName']
        except:
            TV_title = "NOT_FOUND"

        try:
            show = tvdb.Series(ID)
            posters = show.Images.poster()

            TV_poster = "https://www.thetvdb.com/banners/" + str(posters[0]['fileName'])
            # print(TV_poster)
        except:
            TV_poster = ""

        TV_plot = "NOT_FOUND"
        try:
            TV_plot = TVDB_DATA['overview']
        except:
            TV_plot = "NOT_FOUND"

        TV_plot = TV_plot[:400]

        # Destination Location get from database and join the path
        temp = category_choosen
        TV_category = category_choosen
        destination_location = CategoryForTv.objects.get(category_name = category_choosen)
        destination_location = destination_location.initial_path

        try:
            datestr = TVDB_DATA['firstAired']
            year = datestr.split('-',1) # Spliting the date into year -> 2018-01-28
            year = year[0]
        except:
            year = "1800"


        try:
            GENRE = TVDB_DATA['genre']
        except:
            GENRE = "NOT_FOUND"

        try:
            RATING = TVDB_DATA['siteRating']
        except:
            RATING = 0.0

        key = TMDBAPIDetails.objects.get(pk=2).API_KEY
        NOS = 0
        try:
            # Finding no. of seasons
            tvdb.KEYS.API_KEY = key
            show = tvdb.Series(ID)
            allEpisodes = show.Episodes.all()
            mn = 123412341 # minimum season_number
            mx = -12341234 # maximum season_number
            for x in allEpisodes:
                tmp = x['airedSeason']
                mn = min(mn,tmp)
                mx = max(mx,tmp)
            NOS = mx

        except:
            return "EROR"

        # save TV id with a pre-string tv-12356. To avoid conflicts
        if not ID.startswith("tv-"): # means ID is empty now
            ID = "tv-" + ID

        destination_location = destination_location + "/" +  str(year) + "/" + slugify(TV_title) + " " + str(year)
        # Build json Data
        # print(TV_WRITER)


        form_TVDB = {
            'TV_title': TV_title,
            'TV_id': ID,
            'year': year,
            'genre': GENRE,
            'rating': RATING,
            'writer': TV_WRITER,
            'noOfSeason': NOS,
            'seriesYear': year,
            'cast': TV_CAST,
            'plot': TV_plot,
            'img' : TV_poster,
            'moviecategory': category_choosen,
            'api': API_choosen,
            'destination': destination_location,
        }
        # print("TESTSTDFDDF ->" , form_TMDB)
        return form_TVDB
    else:
        return "EROR"


















############################## Save Movie Infomation ####################


def newEpisode( TV_titles, season_ids,
                episode_serials, episode_ids,
                episode_titles, episode_air_dates, plots,
                filepaths,destination_locations,
                API_Names,is_featureds,is_converteds,
                ratings,is_uploadeds ):

    try:
        # print(season_ids,episode_serials,episode_ids,episode_titles,
        #         episode_air_dates, plots,ratings )
        # UploadEpisode.objects.create(
        # if no information is found default informations will be saved
        uploda = UploadEpisode(
            TV_title = TV_titles,
            season_ID = season_ids ,
            episode_ID = episode_ids ,
            episode_serial = episode_serials,
            episode_title = episode_titles,
            episode_air_date = episode_air_dates ,
            plot = plots ,
            filepath = filepaths,
            destination_location = destination_locations,
            is_featured = is_featureds,
            is_converted = is_converteds,
            is_uploaded = is_uploadeds,
            rating = ratings,
            API_name = API_Names,
            episode_api_ID = "" # initially I don't know the episode ip
        )
        uploda.save()
        return "OK"
    except:
        print("Why the fuck",season_ids,episode_ids)
        return "EROR"




def newSeason( TvTitle, ID, seasonID , NOReleased, NOUploaded, DLocation, API_Name):
    try:
        # print(TvTitle,ID,seasonID,NOReleased,NOUploaded,DLocation,API_Name)
        # CreateSeason.objects.create(
        # print("safd",DLocation)
        if not os.path.exists( DLocation+"/"):
            os.makedirs( DLocation+"/")

        uploda = CreateSeason(
            TV_title = TvTitle,
            TV_ID = ID,
            season_id = seasonID ,
            destination_location =  DLocation,
            numberOfReleased = NOReleased,
            numberOfUploaded = NOUploaded ,# initiali No episodes are uploaded
            API_name = API_Name,
        )
        uploda.save()
        # print("Saved ", seasonID)
        return "SAVED"
    except:
        return "EROR"





def getTVSeason(seasonID,ID):
    S = CreateSeason.objects.get( TV_ID = ID , season_id = seasonID )  #pk = primary key
    return S



def saveIMDB_seasons_episodes( TV_ID, TV_TITLE ):

    ia = IMDb()
    series = ia.get_movie(TV_ID[2:])
    ia.update(series, 'episodes')
    seasons = sorted(series['episodes'].keys())
    NOS = 0

    # count Real Number of seasons, in some cases -1 is provided for unknown season
    # print("sess",seasons)
    for ct in seasons:
        if int(ct) > 0:
            NOS += 1

    # WhichSeries = CreateTVSeries.objects.get( Q (TV_id__icontains=TV_ID) | Q(TV_title__icontains=TV_TITLE))
    # print("fuck")
    WhichSeries = CreateTVSeries.objects.get( TV_id=TV_ID ,TV_title__icontains=TV_TITLE)
    destlocation = str(WhichSeries.destination_location)
    # print("NOS",NOS)

    for sesn in range(1,NOS+1):
    #     #obj, seasonID , NOReleased, NOUploaded, DLocation, API_Name

        episodes = len(series['episodes'][sesn])
        seasonID = "Season "+ str(sesn)
        # dest_location = destlocation + "/" + seasonID + "/"
        dest_location = destlocation + "/" + seasonID
        # print("dl",destlocation)

        status = newSeason(WhichSeries,TV_ID,seasonID,int(episodes), 0, dest_location,"IMDB")

        if status == "EROR":
            return False
        else:
            # save epispdes
            # imdb data has problems, sometimes indexing starts from 1, and sometimes starts from 0
            # handeling that situation by try catch

            try:
                x = series['episodes'][sesn]
                lw = 1000000001
                hi = -500000000
                for y in x:
                    lw = min(lw,int(y))
                    hi = max(hi,int(y))
            except:
                lw = 1
                hi = episodes+1

            for epsd in range(lw, hi+1):
                manual_episode_id = makeEpisodeId(TV_ID,sesn,epsd)
                info = series['episodes'][sesn][epsd]
                epsd_dest_location = dest_location + "/" # check FTP pathing with destination

                try:
                    epsd_title = info.get('title')
                except:
                    epsd_title = "Not Found"

                try:
                    epsd_rating = info.get('rating')
                except:
                    epsd_rating = 0.0
                try:
                    epsd_air_date = info.get('original air date')
                except:
                    epsd_air_date = "Not Found"
                try:
                    epsd_plot= info.get('plot')
                except:
                    epsd_plot= "Not Found"

                if epsd_rating is None:
                    epsd_rating = 0.0

                S = getTVSeason(seasonID,TV_ID)

                # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
                #         epsd_plot, epsd_dest_location,epsd_rating )
                # # saving the episode information into the models
                # if any error occurs while saving function will return to views.py
                state = newEpisode(WhichSeries,S,epsd,manual_episode_id,
                    str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
                    str(epsd_dest_location),"IMDB", False, False, epsd_rating, False )

                # print(S, state)

                if state  == "EROR":
                    return False
    #means all available seasons and episode info saved to model
    return True










################################## Saving all TMDB informations ##############################
def newEpisodeTMDB( TV_titles, season_ids,
                episode_serials, episode_ids,
                episode_titles, episode_air_dates, plots,
                filepaths,destination_locations,
                API_Names,is_featureds,is_converteds,
                ratings,is_uploadeds,epsdapiid ):

    try:
        # print(season_ids,episode_serials,episode_ids,episode_titles,
        #         episode_air_dates, plots,ratings )
        # UploadEpisode.objects.create(
        # if no information is found default informations will be saved
        uploda = UploadEpisode(
            TV_title = TV_titles,
            season_ID = season_ids ,
            episode_ID = episode_ids ,
            episode_serial = episode_serials,
            episode_title = episode_titles,
            episode_air_date = episode_air_dates ,
            plot = plots ,
            filepath = filepaths,
            destination_location = destination_locations,
            is_featured = is_featureds,
            is_converted = is_converteds,
            is_uploaded = is_uploadeds,
            rating = ratings,
            API_name = API_Names,
            episode_api_ID = epsdapiid # initially I don't know the episode ip
        )
        uploda.save()
        return "SAVED"
    except:
        # print("Why the fuck",season_ids,episode_ids)
        return "EROR"


def get_TMDBEpisodeInfo(id,season_number):

    tmdb.API_KEY =  getTMDB_APIKEY()
    # print(tmdb.API_KEY)
    tv_seasons = tmdb.TV_Seasons(id, season_number)
    response = tv_seasons.info()
    # print("how")
    return response['episodes']



def saveTMDB_seasons_episodes( TV_ID, TV_TITLE ):

    seriesInfo = get_TMDB_by_ID(TV_ID)
    seasons = seriesInfo['seasons']
    # WhichSeries = CreateTVSeries.objects.get( Q (TV_id__icontains=TV_ID) | Q(TV_title__icontains=TV_TITLE))

    WhichSeries = CreateTVSeries.objects.get( TV_id=TV_ID  ,TV_title=TV_TITLE, API_name = "TMDB" )
    destlocation = str(WhichSeries.destination_location)

    lw = 1234123412
    hi = -12341234123

    for sesn in seasons:
    #     #obj, seasonID , NOReleased, NOUploaded, DLocation, API_Name
        episodes = sesn['episode_count']
        seasonID = "Season "+ str( sesn['season_number'] )
        dest_location = destlocation + "/" + seasonID
        print(dest_location)
        if not os.path.exists( dest_location ):
            os.makedirs( dest_location )
        lw = min( lw, sesn['season_number'] )
        hi = max( hi, sesn['season_number'] )
        status = newSeason(WhichSeries,TV_ID,seasonID,int(episodes), 0, dest_location,"TMDB")

        if status == "EROR":
            return False

            #save epispdes
            # imdb data has problems, sometimes indexing starts from 1, and sometimes starts from 0
            # handeling that situation by try catch


    #fetching all episodes information
    sesn = None
    for sesn in range(lw,hi+1):
        epsds = get_TMDBEpisodeInfo(TV_ID,sesn)
        seasonID = "Season "+ str( sesn )

        for info in epsds:
            epsd = info.get('episode_number')
            manual_episode_id = makeEpisodeId(TV_ID,sesn,int(epsd))
            epsd_dest_location = dest_location + "/" # check FTP pathing with destination

            try:
                epsd_title = info.get('name')
            except:
                epsd_title = "Not Found"

            try:
                epsd_rating = info.get('vote_average')
            except:
                epsd_rating = 0.0
            try:
                epsd_air_date = info.get('air_date')
            except:
                epsd_air_date = "Not Found"
            try:
                epsd_plot= info.get('overview')
            except:
                epsd_plot= "Not Found"

            try:
                epsd_api_id= info.get('id')
            except:
                epsd_api_id= "Not Found"

            if epsd_rating is None:
                epsd_rating = 0.0

            S = getTVSeason(seasonID,TV_ID)

            # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
            #         epsd_plot, epsd_dest_location,epsd_rating )
            # # saving the episode information into the models
            # if any error occurs while saving function will return to views.py
            state = newEpisodeTMDB(WhichSeries,S,int(epsd),manual_episode_id,
                str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
                str(epsd_dest_location),"TMDB", False, False, epsd_rating, False,epsd_api_id )

            if state  == "EROR":
                    return False
    #means all available seasons and episode info saved to model
    return True










###########################################################



def saveTVDB_seasons_episodes( TV_ID, TV_TITLE ):

    try:
        key = TMDBAPIDetails.objects.get(pk=2).API_KEY

        tvdb.KEYS.API_KEY = key
        if TV_ID.startswith('tv-'):
            show = tvdb.Series(TV_ID[3:])
        else:
            show = tvdb.Series(TV_ID)

        tv = show.info()
        allEpisodes = show.Episodes.all() # only episodes are fetchable from tvdb
        # print(key)
    except:
        return "EROR"
    # WhichSeries = CreateTVSeries.objects.get( Q (TV_id__icontains=TV_ID) | Q(TV_title__icontains=TV_TITLE))

    WhichSeries = CreateTVSeries.objects.get( TV_id=TV_ID  ,TV_title=TV_TITLE, API_name = "TVDB" )
    destlocation = str(WhichSeries.destination_location)

    lw = 1234123412
    hi = -12341234123

    mn = 123412341 # minimum season_number
    mx = -12341234 # maximum season_number

    release_episodes = {} # { seaons number : episode.count }

    for x in allEpisodes:
        tmp = x['airedSeason']
        mn = min(mn,tmp)
        mx = max(mx,tmp)

    for y in allEpisodes:
        tmp = y['airedSeason']
        try:
            release_episodes[str(tmp)] = int( release_episodes[str(tmp)] )  + 1
        except:
            release_episodes[str(tmp)] = 1


    # saving all the season information
    for x in release_episodes:
        NOE = release_episodes[x] # Number of episode
        seasonID = "Season "+ str( x )
        dest_location = destlocation + "/" + seasonID
        if not os.path.exists( dest_location ):
            os.makedirs( dest_location )
        status = newSeason(WhichSeries,TV_ID,seasonID,int(NOE), 0, dest_location,"TVDB")
        if status == "EROR":
            return False



    # #fetching all episodes information
    for info in allEpisodes:
        seasonID = "Season "+ str( info['airedSeason'] )
        epsd = info.get('airedEpisodeNumber')
        manual_episode_id = makeEpisodeId(TV_ID,int(info['airedSeason']),int(epsd))
        epsd_dest_location = dest_location + "/"  # check FTP pathing with destination

        try:
            epsd_title = info.get('episodeName')
        except:
            epsd_title = "Not Found"

        try:
            epsd_rating = info.get('siteRating')
        except:
            epsd_rating = 0.0
        try:
            epsd_air_date = info.get('firstAired')
        except:
            epsd_air_date = "Not Found"
        try:
            epsd_plot= info.get('overview')
        except:
            epsd_plot= "Not Found"

        try:
            epsd_api_id= info.get('id')
        except:
            epsd_api_id= "Not Found"

        if epsd_rating is None:
            epsd_rating = 0.0

        S = getTVSeason(seasonID,TV_ID)

        # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
        #         epsd_plot, epsd_dest_location,epsd_rating )
        # # saving the episode information into the models
        # if any error occurs while saving function will return to views.py
        state = newEpisodeTMDB(WhichSeries,S,int(epsd),manual_episode_id,
            str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
            str(epsd_dest_location),"TVDB", False, False, epsd_rating, False,epsd_api_id )

        if state  == "EROR":
                return False
    # #means all available seasons and episode info saved to model
    return True










###########################################################


def saveTVInformation(request,category_choosen ):

    url = request.POST.get('poster_path')
    if url.startswith('http'):
        try:
            TV_ID = request.POST.get('TV_id')
            cat_ID = CategoryForTv.objects.get(category_name=category_choosen)
            TV_TITLE = request.POST.get('TV_title')
            YEAR = request.POST.get('year')
            GENRE = request.POST.get('genre')
            RATING = request.POST.get('rating')
            NOS = request.POST.get('noOfSeason') # Number of season
            WRITER = request.POST.get('writer')
            seriesYears = request.POST.get('TV_timeline')
            CAST = request.POST.get('cast')
            PLOT = request.POST.get('plot')
            API_NAME = request.POST.get('API_name')
            IS_FEATURED = request.POST.get('isFeatured')
            DESTINATION_LOCATION = request.POST.get('destination_location')


            uploadInfo = CreateTVSeries(
                TV_id = TV_ID,
                category_id = cat_ID,
                TV_title = TV_TITLE,
                year = YEAR ,
                TV_timeline = seriesYears,
                numberOfSeason = NOS,
                genre = GENRE,
                rating = RATING ,
                writer = WRITER ,
                cast = CAST  ,
                plot = PLOT,
                API_name = API_NAME,
                is_featured = IS_FEATURED,
                destination_location = DESTINATION_LOCATION,
            )
            uploadInfo.save()


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
            path = os.path.join(TV_TITLE)
            img_data = requests.get(image_url).content
            posterlocation = DESTINATION_LOCATION + "/poster"
            # print("Modified ",posterlocation)
            npath = posterlocation + "/" + TV_ID + "_" + slugify(TV_TITLE) +  '.jpg'


            if not os.path.exists( posterlocation ):
               os.makedirs( posterlocation )

            with open( npath, 'wb') as handler:
                handler.write( img_data )

            uploadInfo.poster_path = npath
            uploadInfo.save();
            img_temp.flush()
            # messages.success(request, 'Your Data is saved Successfully!')

            # if all TV series + episodes + seasons information saved Successfully this method will return True
            if API_NAME == 'IMDB':
                return saveIMDB_seasons_episodes(TV_ID,TV_TITLE)
            elif API_NAME == 'TMDB':
                return saveTMDB_seasons_episodes(TV_ID,TV_TITLE)
            elif API_NAME == 'TVDB':
                return saveTVDB_seasons_episodes(TV_ID,TV_TITLE)

        except:
            return False
    else:
        # save Manual Data

        try:
            manualImage = request.FILES.get('manualImageFile') # Manual poster
            extension = str(manualImage).split('.')[1]
            TV_ID = request.POST.get('TV_id')
            cat_ID = CategoryForTv.objects.get(category_name=category_choosen)
            TV_TITLE = request.POST.get('TV_title')
            YEAR = request.POST.get('year')
            GENRE = request.POST.get('genre')
            RATING = request.POST.get('rating')
            NOS = request.POST.get('noOfSeason') # Number of season
            WRITER = request.POST.get('writer')
            seriesYears = request.POST.get('TV_timeline')
            CAST = request.POST.get('cast')
            PLOT = request.POST.get('plot')
            API_NAME = request.POST.get('API_name')
            IS_FEATURED = request.POST.get('isFeatured')
            DESTINATION_LOCATION = request.POST.get('destination_location')



            uploadInfo = CreateTVSeries(
                TV_id = TV_ID,
                category_id = cat_ID,
                TV_title = TV_TITLE,
                year = YEAR ,
                TV_timeline = seriesYears,
                numberOfSeason = NOS,
                genre = GENRE,
                rating = RATING ,
                writer = WRITER ,
                cast = CAST  ,
                plot = PLOT,
                API_name = API_NAME,
                is_featured = IS_FEATURED,
                destination_location = DESTINATION_LOCATION,
            )
            uploadInfo.save()
            # print("MOVIE SAVED")
            posterlocation = DESTINATION_LOCATION + "/poster"
            npath = posterlocation + "/" +  slugify(TV_TITLE) +  '.' + extension;

            if not os.path.exists( posterlocation ):
               os.makedirs( posterlocation )

            uploadInfo.poster_path = manualImage #Saving manual Image
            uploadInfo.save();


            return True

        except:
            return False











################################ RAW method Section #################



############################################### starting Episode Searching ###################################

def isNewEpisodeFound(tv, tvid, seasonid, api):
    tv = tv.rsplit(' ',1)[0] # Removing last word "game of thrones tt1234" > game of thrones
    if api == 'IMDB':
        # get tv details
        ia = IMDb()
        series = ia.get_movie(tvid[2:])
        ia.update(series, 'episodes')
        sesn = seasonid.split(' ')[1]
        found = len(series['episodes'][int(sesn)])
        api_got_seasons = series['episodes'][int(sesn)]
        savedEpisode = UploadEpisode.objects.filter( TV_title__TV_title = tv, episode_ID__contains = tvid, season_ID__season_id = seasonid )
        available = savedEpisode.count()
        destlocation = str( CreateTVSeries.objects.get( TV_id = tvid ).destination_location )

        if available == found:
            return "EQUAL"
        else:

            # add code for if imdb fuckingly starts episode indexing from xero.

            list = []
            for x in savedEpisode:
                number = x.episode_serial
                list.append(number)
            list = sorted(list)
            print(list)

            missingEpisode = []
            for e in api_got_seasons:
                if(int(e) not in list):
                    missingEpisode.append(int(e))

            # print(missingEpisode)

            # print("season ", sesn)

            # try:
            #     x = api_got_seasons
            #     # print("asd",x)
            #     lo = 1000000001
            #     hi = -500000000
            #     for y in x:
            #         lo = min(lo,int(y))
            #         hi = max(hi,int(y))
            #     print("asdf",lo,hi)
            #     for y in range(lo,hi+1):
            #         if (int(y) not in list):
            #             missingEpisode.append(i)
            # except:
            #     lo = 1
            #     hi = found + 1

            # print(missingEpisode)

            WhichSeries = CreateTVSeries.objects.get( TV_id__exact = tvid, TV_title__exact= tv)
            # dest_location = destlocation + "/" + seasonid
            dest_location = os.path.join(destlocation , seasonid)

            for epsd in missingEpisode:
                manual_episode_id = makeEpisodeId(tvid,int(sesn),epsd)
                info = series['episodes'][int(sesn)][int(epsd)]
                epsd_dest_location = os.path.join(dest_location)  # check FTP pathing with destination

                try:
                    epsd_title = info.get('title')
                except:
                    epsd_title = "Not Found"

                try:
                    epsd_rating = info.get('rating')
                except:
                    epsd_rating = 0.0
                try:
                    epsd_air_date = info.get('original air date')
                except:
                    epsd_air_date = "Not Found"
                try:
                    epsd_plot= info.get('plot')
                except:
                    epsd_plot= "Not Found"

                if epsd_rating is None:
                    epsd_rating = 0.0

                S = getTVSeason(seasonid,tvid)
    #                 # print(S)
    #
    #                 # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
    #                 #         epsd_plot, epsd_dest_location,epsd_rating )
    #                 # # saving the episode information into the models
    #                 # if any error occurs while saving function will return to views.py
                state = newEpisode(WhichSeries,S,epsd,manual_episode_id,
                    str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
                    str(epsd_dest_location),"IMDB", False, False, epsd_rating, False )

                if state == "EROR":
                    return False

        return True
    elif api == 'TMDB':
        # get tv details
        # print(tv,tvid,seasonid,api)
        seasonID =  seasonid
        sesn = seasonID.split(' ')[1]
        epsds = get_TMDBEpisodeInfo( tvid,int(sesn) )
        # print("sadf")
        WhichSeries = CreateTVSeries.objects.get(TV_id=tvid,TV_title=tv)
        sesn = CreateSeason.objects.get(TV_title__TV_title = tv, season_id = seasonID, TV_ID= tvid )
        dest_location = sesn.destination_location
        # print("whichfuck",sesn,WhichSeries.TV_id)
        status = lookForTMDBEpisode(epsds,tvid,seasonID,WhichSeries,dest_location)

        if status == "EROR":
            return False
        else:
            return True

    elif api == 'TVDB':

        seasonID =  seasonid
        sesn = seasonID.split(' ')[1]

        try:
            key = TMDBAPIDetails.objects.get(pk=2).API_KEY
            tvdb.KEYS.API_KEY = key

            if tvid.startswith('tv-'):
                show = tvdb.Series(tvid[3:])
            else:
                show = tvdb.Series(tvid)
            allEpisodes = show.Episodes.all() # only episodes are fetchable from tvdb
            # print(key)
        except:
            return False


        WhichSeries = CreateTVSeries.objects.get(TV_id=tvid,TV_title=tv)
        sesn = CreateSeason.objects.get(TV_title__TV_title = tv, season_id = seasonID, TV_ID= tvid )
        dest_location = WhichSeries.destination_location
        # print("whichfuck",sesn,WhichSeries.TV_id)
        status = lookForTVDBEpisode(allEpisodes,tvid,seasonID,WhichSeries,dest_location)

        if status == "EROR":
            return False
        else:
            return True



###################################################### ending episode searching ####################################


###################################################### Starting Season searching ####################################


#check if the Season existing in the model or not
def isSeasonInModel( sesn , tvid ):
    # print(sesn['season_number'] )
    try:
        # Checking if the season object is in the model or not
        grabObj = CreateSeason.objects.get( TV_ID = tvid, season_id = str( "Season " + str(sesn['season_number']) ))
        return "FOUND"
    except:
        return "NOTFOUND"
        # print("hmmmmm")

def seasonFound( sesn , tvid ):
    # print(sesn['season_number'] )
    try:
        # Checking if the season object is in the model or not
        grabObj = CreateSeason.objects.get( TV_ID = tvid, season_id = str( "Season " + str(sesn) ))
        return "FOUND"
    except:
        return "NOTFOUND"
        # print("hmmmmm")



#check if the episode existing in the model or not
def isEpisodeInModel(sesn, WhichSeries, episodesrl ):
    try:
        grabObj = UploadEpisode.objects.get( TV_title=WhichSeries, season_ID__season_id = sesn , episode_serial= episodesrl)
        return "FOUND"
    except:
        return "NOTFOUND"
        # print("hmmmmm")


def getAllEpisodes(season):
    # print("helel",UploadEpisode.objects.filter(episode_ID__startswith = season) )
    obj = UploadEpisode.objects.filter(episode_ID__startswith = str(season))
    return obj



def lookForTMDBEpisode( epsds,tvid,seasonID, WhichSeries,dest_location ):

    for info in epsds:
        epsd = info.get('episode_number')
        sesn = seasonID.split(' ')[1]
        manual_episode_id = makeEpisodeId(tvid,int(sesn),int(epsd))
        epsd_dest_location = os.path.join(dest_location) # check FTP pathing with destination


        if (isEpisodeInModel(seasonID,WhichSeries,int(epsd)) == "NOTFOUND"):
            try:
                epsd_title = info.get('name')
            except:
                epsd_title = "Not Found"

            try:
                epsd_rating = info.get('vote_average')
            except:
                epsd_rating = 0.0
            try:
                epsd_air_date = info.get('air_date')
            except:
                epsd_air_date = "Not Found"
            try:
                epsd_plot= info.get('overview')
            except:
                epsd_plot= "Not Found"

            try:
                epsd_api_id= info.get('id')
            except:
                epsd_api_id= "Not Found"

            if epsd_rating is None:
                epsd_rating = 0.0

            S = getTVSeason(seasonID,tvid)

            # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
            #         epsd_plot, epsd_dest_location,epsd_rating )
            # # saving the episode information into the models
            # if any error occurs while saving function will return to views.py
            state = newEpisodeTMDB(WhichSeries,S,int(epsd),manual_episode_id,
                str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
                str(epsd_dest_location),"TMDB", False, False, epsd_rating, False,epsd_api_id )

            if state  == "EROR":
                return "EROR"


###########################################################################################################


def lookForTVDBEpisode( allEpisodes,tvid,seasonID, WhichSeries,dest_location ):

    for info in allEpisodes:
        seasonID = "Season "+ str( info['airedSeason'] )
        epsd = info.get('airedEpisodeNumber')
        manual_episode_id = makeEpisodeId( tvid, int( info['airedSeason'] ), int(epsd) )
        # epsd_dest_location = dest_location + "/" + seasonID + "/" # check FTP pathing with destination
        epsd_dest_location = os.path.join(dest_location,seasonID) # check FTP pathing with destination

        if( isEpisodeInModel(seasonID, WhichSeries, epsd) == 'NOTFOUND' ):
            print(epsd)
            try:
                epsd_title = info.get('episodeName')
            except:
                epsd_title = "Not Found"

            try:
                epsd_rating = info.get('siteRating')
            except:
                epsd_rating = 0.0
            try:
                epsd_air_date = info.get('firstAired')
            except:
                epsd_air_date = "Not Found"
            try:
                epsd_plot= info.get('overview')
            except:
                epsd_plot= "Not Found"

            try:
                epsd_api_id= info.get('id')
            except:
                epsd_api_id= "Not Found"

            if epsd_rating is None:
                epsd_rating = 0.0

            S = getTVSeason(seasonID,tvid)

            # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
            #         epsd_plot, epsd_dest_location,epsd_rating )
            # # saving the episode information into the models
            # if any error occurs while saving function will return to views.py
            state = newEpisodeTMDB(WhichSeries,S,int(epsd),manual_episode_id,
                str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
                str(epsd_dest_location),"TVDB", False, False, epsd_rating, False,epsd_api_id )

            if state  == "EROR":
                    return "EROR"
    # #means all available seasons and episode info saved to model
    return "Ok"



#############################################################################################


def getLocation(tvid,title,api):
    # print("what the",tvid,title,api)
    loc = CreateTVSeries.objects.get( pk = tvid )
    # print("eitad",loc)
    dlocation = loc.destination_location
    return dlocation


def isNewSeasonFound( tv, tvid, api ):
    if api == 'IMDB':
        # get tv details
        # print(tv,tvid,api)
        # print("fucking-> ",CreateTVSeries.objects.get( TV_id__exact = tvid ,TV_title= tv))
        # destlocation = CreateTVSeries.objects.get( TV_id__exact = tvid ,TV_title= tv).destination_location
        # print(destlocation)
        # destlocation = getLocation(tvid,tv,api)

        ia = IMDb()
        series = ia.get_movie(tvid[2:])
        ia.update(series, 'episodes')
        seasons = sorted(series['episodes'].keys())
        savedSeason = CreateSeason.objects.filter( TV_ID__exact = tvid )
        available = savedSeason.count()
        destlocation = getLocation(tvid,tv,api)


        NOS = 0
        for ct in seasons:
            if int(ct) > 0:
                NOS += 1
        seasons = NOS


        if available == seasons:
            return "EQUAL"
        else:
            list = []
            for x in savedSeason:
                number = x.season_id.split(' ')[1]
                list.append(number)
            list = sorted(list)

            # Seasons list that are not available
            # in some cases season can be start from zer0... fix that here
            missingSeason = []
            for i in range(1, NOS+1 ):
                if str(i) not in list:
                    missingSeason.append(int(i))
            # print("MsdS",missingSeason,tvid,tv)


            WhichSeries = CreateTVSeries.objects.get( TV_id = tvid )

            for sesn in missingSeason:
                episodes = len(series['episodes'][int(sesn)])
                seasonID = "Season " + str(sesn)
                # dest_location = destlocation + "/" + seasonID + "/"
                dest_location = os.path.join(destlocation,seasonID)
                status = newSeason(WhichSeries, tvid, seasonID, int(episodes), 0, dest_location, "IMDB" )
                # print(status)

                if status == "EROR":
                    return "EXISTS"
                else:
                    #save epispdes
                    # imdb data has problems, sometimes indexing starts from 1, and sometimes starts from 0
                    # handeling that situation by try catch

                    try:
                        x = series['episodes'][sesn]
                        lw = 1000000001
                        hi = -500000000
                        for y in x:
                            lw = min(lw,int(y))
                            hi = max(hi,int(y))
                    except:
                        lw = 1
                        hi = episodes+1

                    for epsd in range(lw, hi+1):
                        manual_episode_id = makeEpisodeId(tvid,sesn,epsd)
                        info = series['episodes'][sesn][epsd]
                        epsd_dest_location = os.path.join(dest_location) # check FTP pathing with destination

                        try:
                            epsd_title = info.get('title')
                        except:
                            epsd_title = "Not Found"

                        try:
                            epsd_rating = info.get('rating')
                        except:
                            epsd_rating = 0.0
                        try:
                            epsd_air_date = info.get('original air date')
                        except:
                            epsd_air_date = "Not Found"
                        try:
                            epsd_plot= info.get('plot')
                        except:
                            epsd_plot= "Not Found"

                        if epsd_rating is None:
                            epsd_rating = 0.0

                        S = getTVSeason(seasonID,tvid)
                        # print(epsd,manual_episode_id,epsd_title,epsd_air_date,
                        #         epsd_plot, epsd_dest_location,epsd_rating )
                        # # saving the episode information into the models
                        # if any error occurs while saving function will return to views.py
                        state = newEpisode(WhichSeries,S,epsd,manual_episode_id,
                            str(epsd_title),str(epsd_air_date),str(epsd_plot),str(epsd_dest_location),
                            str(epsd_dest_location),"IMDB", False, False, epsd_rating, False )
                        # print(state)
                            # print("saved")
                        if state == "EROR":
                            return False

        return True
    elif api == 'TMDB':

        seriesInfo = get_TMDB_by_ID(tvid)
        seasons = seriesInfo['seasons']
        NOS = 0
        for x in seasons:
            NOS = NOS + 1

        savedSeason = CreateSeason.objects.filter( TV_ID = tvid )
        available = savedSeason.count()
        destlocation = str(CreateTVSeries.objects.get( TV_id = tvid ).destination_location)
        found = NOS+1

        # print("xyz",found,available,NOS)

        if found == available:
            return True
        elif available < found:
            lw = 1234123412
            hi = -12341234123

            WhichSeries = CreateTVSeries.objects.get( TV_id=tvid, API_name ="TMDB")
            # print("WhichSeries)
            for sesn in seasons:
                if ( isSeasonInModel(sesn,tvid) == "NOTFOUND" ) :
                    # print(sesn)
                    episodes = sesn['episode_count']
                    seasonID = "Season "+ str( sesn['season_number'] )
                    # dest_location = destlocation + "/" + seasonID + "/"
                    dest_location = os.path.join(destlocation,seasonID)
                    lw = min( lw, sesn['season_number'] )
                    hi = max( hi, sesn['season_number'] )
                    status = newSeason(WhichSeries,tvid,seasonID,int(episodes), 0, dest_location,"TMDB")

                    if status == "EROR":
                        return False

                    epsds = get_TMDBEpisodeInfo(tvid,int(sesn['season_number']))
                    status = lookForTMDBEpisode(epsds,tvid,seasonID,WhichSeries,dest_location)
                    if status == "EROR":
                        return False


        return True
    elif api == 'TVDB':
        try:
            key = TMDBAPIDetails.objects.get(pk=2).API_KEY

            tvdb.KEYS.API_KEY = key
            if tvid.startswith('tv-'):
                show = tvdb.Series(tvid[3:])
            else:
                show = tvdb.Series(tvid)

            allEpisodes = show.Episodes.all() # only episodes are fetchable from tvdb
            # print(tvid)
        except:
            return False

        savedSeason = CreateSeason.objects.filter( TV_ID = tvid )
        available = savedSeason.count()
        destlocation = str(CreateTVSeries.objects.get( TV_id = tvid ).destination_location)

        mn = 123412341 # minimum season_number
        mx = -12341234 # maximum season_number

        release_episodes = {} # { seaons number : episode.count }
        for x in allEpisodes:
            tmp = x['airedSeason']
            mn = min(mn,tmp)
            mx = max(mx,tmp)

            try:
                release_episodes[str(tmp)] = int( release_episodes[str(tmp)] )  + 1
            except:
                release_episodes[str(tmp)] = 1

        found = mx+1

        # print("xyz",found,available,NOS)

        if found == available:
            return "EQUAL"
        elif available < found:
            lw = 1234123412
            hi = -12341234123

            WhichSeries = CreateTVSeries.objects.get( TV_id=tvid, TV_title=tv, API_name ="TVDB")
            for x in release_episodes:
                if ( seasonFound(int(x),tvid ) == "NOTFOUND" ) :
                    # print(x)
                    NOE = release_episodes[x] # Number of episode
                    seasonID = "Season "+ str( x )
                    # dest_location = destlocation + "/" + seasonID + "/"
                    dest_location = os.path.join(destlocation,seasonID)
                    status = newSeason(WhichSeries, tvid, seasonID, int(NOE), 0, dest_location,"TVDB")
                    # print(status)
                    if status == "EROR":
                        return False


            state = lookForTVDBEpisode(allEpisodes,tvid,"",WhichSeries,destlocation)
            if state == "EROR":
                return False

        return True



######################################################################### Ending isSeasonFound   ###############################










################################################## RAW ################################

def makeEpisodeId(tv,season,episode):
    S = "S"
    E = "E"

    if episode > 9:
        E = E + str(episode)
    else:
        E = E + "0" + str(episode)

    if season > 9:
        S = S + str(season)
    else:
        S = S + "0" + str(season)

    return str(tv) + "_" + S + E
