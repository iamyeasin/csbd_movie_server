from django.contrib import admin
from . models import CategoryForTv, UploadEpisode, CreateSeason, CreateTVSeries


class CategoryForTvAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'initial_path',)


class UploadEpisodeAdmin(admin.ModelAdmin):
    list_display = ('episode_ID', 'TV_title','season_ID','episode_serial', 'episode_title', 'episode_air_date', 'filepath', )


class CreateTVSeriesAdmin(admin.ModelAdmin):
    list_display = ('TV_id', 'TV_title', 'category_id', 'numberOfSeason',  'poster_path', )


class CreateSeasonAdmin(admin.ModelAdmin):
    list_display = ('TV_title', 'season_id', 'numberOfReleased','numberOfUploaded' )


admin.site.register(CategoryForTv, CategoryForTvAdmin)
admin.site.register(CreateSeason, CreateSeasonAdmin)
admin.site.register(CreateTVSeries, CreateTVSeriesAdmin)
admin.site.register(UploadEpisode, UploadEpisodeAdmin)
