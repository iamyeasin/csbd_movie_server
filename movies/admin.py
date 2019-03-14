from django.contrib import admin
from . models import Category, UploadMovie,MainFeatureHead


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'initial_path',)


class UploadMovieAdmin(admin.ModelAdmin):
    list_display = ('movie_id', 'category_id', 'movie_title', 'year', 'poster_path', )

class MainFeatureHeadAdmin(admin.ModelAdmin):
    list_display = ('movie_id', )



admin.site.register(Category, CategoryAdmin)
admin.site.register(UploadMovie, UploadMovieAdmin)
admin.site.register(MainFeatureHead, MainFeatureHeadAdmin)
