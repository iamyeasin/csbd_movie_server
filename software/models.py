from django.db import models
from django.template.defaultfilters import slugify


##### Gives a specific path ######
def upload_location(instance, filename):
    return "%s/%s/%s/" % ( instance.destination_path, instance.software_title, filename)


class InitialPath(models.Model):
    category_name = models.CharField(max_length=250)
    initial_path = models.CharField(max_length=250)
    background_image = models.FileField(upload_to=upload_location,max_length=700,blank=True)
    frontpage_feature = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name


class UploadSoftware(models.Model):
    software_id = models.CharField(max_length=20, primary_key=True)
    software_title = models.CharField(max_length=200)
    software_file_size = models.CharField(max_length=20,blank=False)
    destination_path = models.CharField(max_length=400)
    poster_path = models.FileField(upload_to=upload_location,max_length=700)
    file_path = models.CharField(max_length=7024)

    def __str__(self):
        return self.software_title
