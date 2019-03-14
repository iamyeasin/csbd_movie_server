from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
from imdb import IMDb, helpers
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
import json,imdb
from django.core import serializers
from django.http import JsonResponse
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView,ListView,CreateView,DeleteView
from Series.models import *
from .filters import MovieFilter
from movies.methods import get_IMDB_by_Name,get_TMDB_by_Name
import omdb
from django.core import serializers

# Create your views here.

class ListViewMovies(ListView):

    def get(self,request):

        if request.method == "GET":
            id = request.GET.get('tv_id')
            title = request.GET.get('SelectedTV')
            btnclicked = request.GET.get('btnClicked')

            if btnclicked == 'UploadEpisode':
                for x,y in request.GET.items():
                    print(x,y)

            if id:
                season = request.GET.get('SelectedSeason')
                sno = season.split(" ",1) # spliting the season number
                sno = sno[1] #only selecting the season number
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
            else:
                tv = request.GET.get('SelectedTV')
                if tv:
                    tvseason = CreateSeason.objects.filter( TV_title__TV_title__contains=tv ).count()
                    ID = CreateSeason.objects.filter( TV_title__TV_title__contains=tv )
                    data = tvseason
                    ID = ID[0]
                    data2 = ID.TV_ID
                    con = {
                        'tvseason':data,
                        'tvid': data2,
                    }

                    jsonmoviedata = json.dumps(con)
                    return HttpResponse(jsonmoviedata, content_type="application/json")
                # return HttpResponse("ok")
            alltvs = CreateTVSeries.objects.all()
            return render(request, 'testing/uploadmovie_list.html', {'alltv':alltvs })

    # context_object_name = 'episodes'
    # model = UploadEpisode
    # template_name = 'testing/uploadmovie_list.html'
