from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name='TV'

urlpatterns = [
    path('add_TV/',views.UploadTVSeries, name='addTV'),
    path('manual_add_tv/',views.ManualTVCreate, name='manualaddtv'),
    path('upload_episode/',views.UploadEpisodeListView.as_view(), name='uploadepisode'),
    path('create_manual_episode/',views.ManualEpisodeCreate.as_view(), name='uploademanualepisode'),
    path('update_episode/',views.updateEpisode, name='updateepisode'),
    path('create_season/',views.seasons, name='createseason'),
    path('create_manual_season/',views.ManualSeasonCreate.as_view(), name='createmanualseason'),
    path('update_tv/',views.updatetv, name='updatetv'),
    path('gettvinfo/',views.getTvInfo, name='tvinfo'),

]
