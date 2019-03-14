# Create your views here.
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
from movies.methods import *
import json,imdb,re,os,sys,paramiko
import tmdbsimple as tmdb
from imdb import IMDb, helpers
import omdb
from django.views.generic import View,TemplateView,ListView,CreateView,DeleteView
from django.core import serializers
from django.core.files.base import ContentFile
from settings.models import *
from movies.methods import *
from imdb import IMDb, helpers
from . models import *
from . forms import *
import movies
from django.views.generic import ( CreateView, View,TemplateView,ListView,DeleteView, DetailView )

######################################################################



# Upload TV series Manually using generic view django
def ManualTVCreate(request):

    if request.method == "POST":
        btnClicked = request.POST.get('btnClicked')
        # Saving TV information
        if btnClicked == 'savetvinfo':
            key = request.POST.get('category')
            category_choosen =  CategoryForTv.objects.get(pk=int(key)).category_name
            status = methods.saveTVInformation(request,category_choosen)
            print(status)
            if status == True:
                return HttpResponse("ok")
            else:
                # print("movie transferred but couldn't save the information")
                return HttpResponseNotFound("Couldn't save the movie information")
        elif btnClicked == 'categorypk':
            key = request.POST.get('category')
            baselocation = CategoryForTv.objects.get(pk=int(key)).initial_path
            data = {"queryset" : baselocation}
            return JsonResponse(data)
    else:
        form = createTVForm()
        baselocation = CategoryForTv.objects.get(pk=1).initial_path # get the base path
        return render(request,'TV/upload_manual_tv.html', {'form':form,'id':baselocation})



class ManualSeasonCreate(CreateView):
    # form_class = createTVForm
    model = CreateSeason
    fields = '__all__'
    # context_object_name = 'createTVForm'
    template_name = 'TV/create_manual_season.html'

    def get_context_data(self,**kwargs):
        baselocation = CategoryForTv.objects.get(pk=1).initial_path
        context = super().get_context_data(**kwargs)
        context['id'] = baselocation
        return  context


class ManualEpisodeCreate(CreateView):
    # form_class = createTVForm
    model = UploadEpisode
    fields = '__all__'
    # context_object_name = 'createTVForm'
    template_name = 'TV/create_manual_episode.html'

    def get_context_data(self,**kwargs):
        baselocation = CategoryForTv.objects.get(pk=1).initial_path
        context = super().get_context_data(**kwargs)
        context['id'] = baselocation
        return  context


#only upload a specific episode
def updateEpisode(request):
    tv = request.GET.get('SelectedTV')
    btnClicked = request.GET.get('btnClicked')

    if btnClicked == 'updateEpisode':

        localpath = request.GET.get('sourcePath')
        filename = request.GET.get('filename')
        convert = request.GET.get('isConverted')
        dlocation = request.GET.get('dlocation')
        epid = request.GET.get('epid')


        # print(localpath,filename,convert,dlocation)

        #first deleting the current file
        filepath = UploadEpisode.objects.get( episode_ID = epid ).filepath
        # calling to take delete action
        status = "OK"
        # status = methods.SFTP_deleteEpisode( filepath )
        # print("1",status)

        # now upload the new file
        if( status == "OK" ):
            # status = movies.methods.SFTPTransferPUT(filename, localpath, dlocation, convert)
            set = UploadEpisode.objects.get( episode_ID = epid )
            set.filepath =  os.path.join(localpath,filename)
            set.save()
            # print("2",status)
            #if successfully uploaded new file
            if( status == "OK" ):
                # print("ok")
                return HttpResponse("OK")
            else:
                return HttpResponseNotFound("NOT FOUND")
        else:
            return HttpResponseNotFound("NOT FOUND")

        pass
    else:
        if tv is not None:
            tvseason = CreateSeason.objects.filter( TV_title__TV_title__contains = tv )
            serialized_qs = serializers.serialize('json', tvseason)
            data = {"queryset" : serialized_qs}
            return JsonResponse(data)
            # return HttpResponse("ok")
            # alltvs = CreateTVSeries.objects.all()
            # return render(request, 'TV/update_episode.html', {'alltv':alltvs })
            # return  render(request,'TV/update_episode.html')
        else:
            alltvs = CreateTVSeries.objects.all()
            return render(request, 'TV/update_episode.html', {'alltv':alltvs })



def updatetv(request):
    form = createTVForm()
    id = request.GET.get('TV_id')
    TV_title = request.GET.get('TV_title')
    btnClicked = request.GET.get('btnclicked')

    if id == "":
        id = None

    if btnClicked == 'searchbtn' and request.method == 'GET':
        tvinfo = None

        if id is None:
            # print("what",id,TV_title)
            # here delete current episode file from ftp



            # then call the upload method to upload the current file

            #
            tvinfo = CreateTVSeries.objects.filter(TV_title=TV_title)
            # tvinfo = tvinfo[0] # grabing the first object
            serialized_qs = serializers.serialize('json', tvinfo)
            data = {"queryset" : serialized_qs} # sending data to html page
            return JsonResponse(data)

        elif id is not None:
            try:
                tvinfo = CreateTVSeries.objects.filter(TV_id= id)
                serialized_qs = serializers.serialize('json', tvinfo)
                data = {"queryset" : serialized_qs} # sending data to html page
                return JsonResponse(data)
            except:
                return HttpResponseNotFound("Data Not Found")
    elif request.method == 'POST':

        id = request.POST.get('TV_id')
        title = request.POST.get('TV_title')

        if id is "": # without id you cannot save or update any data
            return HttpResponseNotFound("EROR")
        else:
            # means id is available

            # try:

                CreateTVSeries.objects.filter(TV_id=id).update(
                    TV_id = request.POST.get('TV_id'),
                    TV_title = request.POST.get('TV_title'),
                    year = request.POST.get('year'),
                    genre = request.POST.get('genre'),
                    rating = request.POST.get('rating'),
                    numberOfSeason = request.POST.get('noOfSeason'),
                    writer = request.POST.get('writer'),
                    TV_timeline = request.POST.get('TV_timeline'),
                    cast = request.POST.get('cast'),
                    plot = request.POST.get('plot'),
                    API_name = request.POST.get('API_name'),
                    is_featured = request.POST.get('isFeatured'),
                )
            # except:
            #     # print("sadf")
            #     return HttpResponseNotFound("EROR")

                manual_poster = request.FILES.get('manualImageFile')

                if manual_poster:
                    print(id)
                    filename = str(manual_poster)
                    extension = filename.split('.')[1]

                    obj = CreateTVSeries.objects.get(TV_id = id )

                    image_path = request.POST.get('destination_location')
                    movie_title = request.POST.get('TV_title')

                    manual_poster_location = image_path + '/poster/' + slugify(movie_title)
                    manual_poster_location = manual_poster_location + '.' + extension
                    # manual_poster_location = manual_poster_location.replace('/','\\')
                    # print(manual_poster_location)
                    # if directory is not available then make the directory
                    if not os.path.exists(image_path + '/poster/'):
                        os.makedirs(image_path + '/poster/')

                    # uploading the manual poster in chunks;
                    with open( manual_poster_location, 'wb+') as destination:
                        for chunk in manual_poster.chunks():
                            destination.write(chunk)

                    CreateTVSeries.objects.filter(TV_id=id).update(poster_path=manual_poster_location)

                    # tv data saved SUCCESFULLY with poster
                    return HttpResponse("OK")
                else:
                    # tv data saved Successfully without images
                    return HttpResponse("OK")


        return HttpResponseNotFound("OK")

    else:
        return  render(request,'TV/update_tv.html',{'form':form})




#Creating TV series Information
def UploadTVSeries(request):
    # Create TV series
    form = createTVForm()
    cats = CategoryForTv.objects.all()

    #means user is trying to fetch Data By ID / Title
    if request.method == 'GET':
        form = createTVForm(request.POST, request.FILES)
        ID = request.GET.get('TV_id')

        #in case ID is not found
        if not ID:
            ID = ""

        ID = ID.lstrip()
        ID = ID.rstrip()
        title = request.GET.get('TV_title')
        if not title:
            title = ""

        title = title.lstrip()
        title = title.rstrip()
        API_choosen = request.GET.get('selectapi')
        category_choosen = request.GET.get('category')
        TV_year = request.GET.get('year')

        #Fetch TV information from IMDB
        if len(ID) > 0 and ID.startswith('tt') and API_choosen == 'IMDB':
            # Getting IMDB Data from the same movies IMDB method
            IMDB_DATA = methods.get_IMDB_by_ID(ID[2:])
            jsonseriesdata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,TV_year)

            if jsonseriesdata != "EROR":
                return HttpResponse(json.dumps(jsonseriesdata), content_type="application/json")
            else:
                messages.error(request,"Data sending problem to the html")
                return HttpResponseNotFound("EROR OCCURED")

        elif API_choosen == 'IMDB' and len(title) > 0 :
            # Search TV by title
            yearGiven = TV_year
            tv_list = methods.get_IMDB_by_Name(title)

            #check if there is any match with year
            for item in tv_list:
                searched_title = item[1]
                ID = item[0]
                # print(ID)

                if yearGiven in searched_title:
                    #Found the movie_TITLE + yearGiven = Matched,There can be multiple, fetching the first one only
                    #Show rest of the list as possible Match
                    ID = item[0]
                    # print(ID)
                IMDB_DATA = methods.get_IMDB_by_ID(ID) # now fetch information with ID

                # if IMDB_DATA is not found
                if IMDB_DATA != "EROR":
                    jsonmoviedata = methods.flyTheInformation(request,IMDB_DATA,ID,API_choosen,category_choosen,TV_year)

                # if IMDB DATA make json
                if jsonmoviedata != "EROR":
                    return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")

            #no data found in the list
            return HttpResponseNotFound("No data found with that Name")
            pass

        elif API_choosen == 'TMDB' and len(ID) > 0:
            #fetching TMDB Data from TMDB API
            TMDB_DATA = methods.get_TMDB_by_ID(ID)
            jsonseriesdata = methods.flyTheInformation( request,TMDB_DATA,ID,API_choosen,category_choosen,TV_year )

            if jsonseriesdata != "EROR":
                return HttpResponse(json.dumps(jsonseriesdata), content_type="application/json")
            else:
                messages.error(request,"Data sending problem to the html")
                return HttpResponseNotFound("EROR OCCURED")

        elif API_choosen == 'TMDB' and len(title) > 0 :
            # Search TV by title
            yearGiven = TV_year
            tv_list = methods.get_TMDB_by_Name(title)

            if tv_list != "EROR":
                #check if there is any match with year
                # print("res" , movie_list.results[0])
                searched_title = tv_list.results[0]['name']
                ID = tv_list.results[0]['id']

                for s in tv_list.results:
                    if yearGiven in s['first_air_date']:
                        searched_title = s['name']
                        ID = s['id']
                TMDB_DATA = methods.get_TMDB_by_ID(ID) # now fetch information with ID
                # if TMDB_DATA is not found
                if TMDB_DATA != "EROR":
                    jsonmoviedata = methods.flyTheInformation(request,TMDB_DATA,ID,API_choosen,category_choosen,TV_year)
                else:
                    return HttpResponseNotFound("EROR OCCURED DURING FIRST FETCH OF IMDB")

                # if TMDB_DATA couldn't make json
                if jsonmoviedata != "EROR":
                    return HttpResponse(json.dumps(jsonmoviedata), content_type="application/json")
                else:
                    return HttpResponseNotFound("EROR OCCURED")
            else:
                return HttpResponseNotFound("EROR")


            pass

        elif API_choosen == 'TVDB' and len(ID) > 0:
            # fetching TVDB Information
            TVDB_DATA = methods.get_TVDB_by_ID(ID)
            jsonseriesdata = methods.flyTheInformation( request,TVDB_DATA,ID,API_choosen,category_choosen,TV_year )

            if jsonseriesdata != "EROR":
                return HttpResponse(json.dumps(jsonseriesdata), content_type="application/json")
            else:
                messages.error(request,"Data sending problem to the html")
                return HttpResponseNotFound("EROR OCCURED")

        return render(request, 'TV/add_TV.html',{'form':form,'cats':cats})


    # means user is trying to save the fetched Data
    if request.method == 'POST':

        category_choosen = request.POST.get('category')
        status = methods.saveTVInformation(request,category_choosen)
        # print(status)
        if status == True:
            return HttpResponse("ok")
        else:
            # print("movie transferred but couldn't save the information")
            return HttpResponseNotFound("Couldn't save the movie information")

    return render(request, 'TV/add_TV.html',{'form':form,'cats':cats})


def seasons(request):

    btnClicked = request.GET.get('btnClicked')
    if btnClicked == 'choosenTV':
        tvtitle = request.GET.get('SelectedTV')
        tvtitle = tvtitle.lstrip()
        # print(tvtitle)


        tvseason = CreateSeason.objects.filter( TV_ID = tvtitle )
        # counting again the upload episodes in every season and saving it to the model based on uploadEpisode.isUploaded =True
        for x in tvseason:
            x.numberOfUploaded = UploadEpisode.objects.filter( episode_ID = tvtitle , season_ID__season_id = x.season_id , is_uploaded = True).count()
            x.save()

        data = tvseason
        # print(data)
        # return HttpResponse("ok")
        serialized_qs = serializers.serialize('json', tvseason)
        data = {"queryset" : serialized_qs} # sending data to html page

        return JsonResponse(data)

    elif btnClicked == 'searchnewseason':
        tvid = request.GET.get('tvid')
        api = request.GET.get('api')
        tvtitle = request.GET.get('SelectedTV')
        # print("bal",tvtitle,tvid)
        status = methods.isNewSeasonFound(tvtitle, tvid, api);

        if status == True:
            return HttpResponse("ok")
        else:
            return HttpResponseNotFound("EROR")
    elif btnClicked == 'deleteSeason':
        try:
            #add FTP code for deleting files from FTP

            id = request.GET.get('tvid')
            season = request.GET.get('sesn')
            api = request.GET.get('api')

            # deleting data from model
            instance = CreateSeason.objects.get(TV_ID=id,season_id=season,API_name=api)
            instance.delete()
            return HttpResponse("Ok")
        except:
            return HttpResponse("Couldn't Delete")
    else:
        alltvs = CreateTVSeries.objects.all()
        return render(request, 'TV/create_new_season.html', {'alltv':alltvs })



class UploadEpisodeListView(ListView):

    def get(self,request):

        if request.method == "GET":
            id = request.GET.get('tv_id')
            title = request.GET.get('SelectedTV')
            btnclicked = request.GET.get('btnClicked')

            if btnclicked == 'UploadEpisode':
                # Means Admin sending location to server to upload movie
                eID = request.GET.get('id')
                set = UploadEpisode.objects.get( episode_ID = eID )
                # remotepath = set.destination_location
                localpath = request.GET.get('sourcePath')
                filename = request.GET.get('filename')
                convert = request.GET.get('isConverted')
                dlocation = request.GET.get('dlocation') # episode location
                # print( "pwd", dlocation )

                # print( localpath,filename)
                # remotepath = "/mnt/English/"

                status = movies.methods.SFTPTransferPUT(filename, localpath, dlocation, convert)
                # print(status)
                #if file needs to convert

                # if( convert == "1" ):
                    # Do the convert
                    # convert_status = convert_file_to_mp4(localpath, filename)

                # set.filepath = set.destination_location +"/"+ filename
                set.filepath = os.path.join( set.destination_location , filename )
                # if convert_status == "OK":
                #     set.is_converted = True
                if status == "OK":
                    set.is_uploaded = True
                    id = eID.split('_')
                    id = id[0]
                    season = set.season_ID
                    tvseason = CreateSeason.objects.get( TV_ID__contains = id,season_id = season)
                    currentEpisodes = tvseason.numberOfUploaded + 1
                    tvseason.numberOfUploaded = currentEpisodes
                    tvseason.save()
                    # dash = CreateSeason( numberOfUploaded = currentEpisodes ,)
                    # dash.save()
                set.save()

                if status != "EROR":
                    return HttpResponse("ok")
                else:
                    return HttpResponseNotFound("Problem during saving the data")

            elif btnclicked == 'deleteEpisode':
                try:
                    epid = request.GET.get('epid')
                    title = request.GET.get('title')
                    api = request.GET.get('api')
                    srl = request.GET.get('srl')
                    filepath = UploadEpisode.objects.get( episode_ID = epid ).filepath
                    tvid = request.GET.get('tvid')
                    sesnid = request.GET.get('sesnid')



                    # Write code for deleting episode from FTP
                    # print(filepath)

                    # calling to take delete action
                    status = methods.SFTP_deleteEpisode( filepath )
                    # return HttpResponseNotFound("ok")
                    # print(status)

                    # delete episode from database/model
                    if( status == "OK" ):
                        instance = UploadEpisode.objects.get( episode_ID=epid, episode_serial=srl, API_name=api )
                        instance.delete()
                        obj = CreateSeason.objects.get( TV_ID = tvid , season_id = sesnid )

                        cur = obj.numberOfUploaded
                        obj.numberOfUploaded = cur-1 # Reducing from seasons number of uploaded
                        # print(cur)
                        obj.save()

                        return HttpResponse("ok")
                    else:
                        return HttpResponseNotFound("Can't Delete")
                except:
                    return HttpResponseNotFound("Can't Delete")

            elif btnclicked == 'searchnewepisode':
                try:
                    status = False
                    tv = request.GET.get('SelectedTV')
                    api = request.GET.get('api')
                    selectedseason = request.GET.get('selectedseason')
                    tvid = request.GET.get('tvid')
                    # print(tv,api,selectedseason,tvid)
                    status = methods.isNewEpisodeFound(tv, tvid, selectedseason, api);
                    # print(status)
                    if status == True:
                        return HttpResponse("ok")
                except:
                    return HttpResponseNotFound("Something is wrong")

            elif id:
                try:
                    season = request.GET.get('SelectedSeason')
                    # print(season)
                    # that sno variable sometimes goest mad. I don't know why the fuck he does that
                    sno = season.split(" ")[1] # spliting the season number
                    # print(sno)
                    #only selecting the season number
                    # make prefix of season id
                    cmp = int(sno)
                    if (cmp > 9):
                        season = id + "_S" + sno
                    else:
                        season = id + "_S0" + sno

                    season = str(season)
                    episodes = UploadEpisode.objects.filter(episode_ID__startswith=season)
                    # return HttpResponse("ok")
                    serialized_qs = serializers.serialize('json', episodes)
                    data = {"queryset" : serialized_qs}
                    return JsonResponse(data)
                except:
                    return HttpResponse("ok")
            else:
                tv = request.GET.get('SelectedTV')
                if tv is not None:
                    tv = tv.lstrip()
                    # print(tv)
                    tvseason = CreateSeason.objects.filter( TV_ID = tv )
                    serialized_qs = serializers.serialize('json', tvseason)
                    data = {"queryset" : serialized_qs}
                    return JsonResponse(data)
                # return HttpResponse("ok")
            alltvs = CreateTVSeries.objects.all()
            return render(request, 'TV/upload_episode.html', {'alltv':alltvs })

    # context_object_name = 'episodes'
    # model = UploadEpisode
    # template_name = 'testing/uploadmovie_list.html'
