from django.contrib import admin
from . models import FTPDetails,TMDBAPIDetails,OMDBAPIDetails,IMDBAPIDetails

class FTPDetailsAdmin(admin.ModelAdmin):
    list_display = ('server_address', 'username', 'portnumber',)


class TMDBAPIDetailsAdmin(admin.ModelAdmin):
    list_display = ('username', 'API_KEY', 'BaseImageLink' )

class OMDBAPIDetailsAdmin(admin.ModelAdmin):
    list_display = ('username','API_KEY',)

class IMDBAPIDetailsAdmin(admin.ModelAdmin):
    list_display = ('MoviePageLink',)


admin.site.register(FTPDetails, FTPDetailsAdmin)
admin.site.register(TMDBAPIDetails, TMDBAPIDetailsAdmin)
admin.site.register(OMDBAPIDetails, OMDBAPIDetailsAdmin)
admin.site.register(IMDBAPIDetails, IMDBAPIDetailsAdmin)
