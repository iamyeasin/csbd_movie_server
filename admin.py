from django.contrib import admin
from . models import UploadSoftware,InitialPath

class UploadSoftwareAdmin(admin.ModelAdmin):
    list_display = ('software_id', 'software_title', 'software_file_size', 'destination_path')

class InitialPathAdmin(admin.ModelAdmin):
    list_display = ('initial_path','category_name')

admin.site.register(UploadSoftware)
admin.site.register(InitialPath)
