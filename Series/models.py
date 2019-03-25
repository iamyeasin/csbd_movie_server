from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
import os,shutil

#Gives a specific path
def upload_location(instance, filename):
    # newname = filename.split('.')[-1]
    year = slugify(instance.year)
    # filename = "%s_%s.%s" % (instance.movie_id, instance.movie_title, newname)
    path = ((instance.category_id.initial_path) + "/" + str(year) + "/" + slugify(instance.TV_title) + " " +
    str(year) + "/poster/" + (filename))

    return path


class CategoryForTv(models.Model):
    category_name = models.CharField(max_length=250)
    initial_path = models.CharField(max_length=250)
    background_image = models.FileField(upload_to=upload_location,max_length=700,blank=True)
    frontpage_feature = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name


class CreateTVSeries(models.Model):
    TV_id = models.CharField(max_length=20, primary_key=True)
    category_id = models.ForeignKey(CategoryForTv,on_delete=models.CASCADE)
    TV_title = models.CharField(max_length=7024)
    year = models.PositiveIntegerField()
    TV_timeline = models.CharField(max_length=50)
    numberOfSeason = models.PositiveIntegerField()
    genre = models.CharField(max_length=7024)
    rating = models.DecimalField(max_digits=5, decimal_places=1,default=None)
    writer = models.CharField(max_length=7024)
    cast = models.CharField(max_length=7024)
    plot = models.CharField(max_length=6600)
    poster_path = models.FileField(upload_to=upload_location,max_length=700)
    destination_location = models.CharField(max_length=7024)
    is_featured = models.BooleanField(default=False)
    API_name = models.CharField(max_length=20)

    def __str__(self):
        return self.TV_title

    def get_absolute_url(self):
        return reverse("TV:manualaddtv",kwargs={'pk':self.pk})


class CreateSeason(models.Model):
    TV_title = models.ForeignKey(CreateTVSeries,on_delete=models.CASCADE,related_name='series')
    season_id = models.CharField(max_length=50) # season_id be like Season 1, Season 2 etc
    destination_location = models.CharField(max_length=7024)
    numberOfReleased = models.PositiveIntegerField()
    numberOfUploaded = models.PositiveIntegerField()
    API_name = models.CharField(max_length=20)
    TV_ID = models.CharField(max_length=50,blank=True)


    def __str__(self):
        return self.season_id

    class Meta:
        unique_together = (('TV_ID', 'season_id'),)

    def get_absolute_url(self):
        # create the season folder inside the /mnt/*
        if not os.path.exists( self.destination_location + "/"):
            print("oikj")
            os.makedirs( self.destination_location +"/")
        return reverse("TV:createseason") # after saving a season where to go


#only Episodes will be uploaded That is why it is UploadEpisode
class UploadEpisode(models.Model):

    TV_title = models.ForeignKey(CreateTVSeries, on_delete=models.CASCADE)
    season_ID = models.ForeignKey(CreateSeason,on_delete=models.CASCADE)
    episode_serial = models.PositiveIntegerField(blank = False)
    #Make episode_id manually , IMDbPy does not providing the id of episodes
    episode_ID = models.CharField(primary_key = True,max_length=50,blank=False) # example - S01E02 -> all caps
    episode_title = models.CharField(max_length=500,blank = True)
    episode_air_date = models.CharField(max_length=500, blank = True )
    plot = models.CharField(max_length=7024 , blank = True)
    filepath = models.CharField(max_length=7024, blank = True )
    destination_location = models.CharField(max_length=7024, blank = True)
    API_name = models.CharField(max_length=50, blank = True)
    episode_api_ID = models.CharField(max_length=100,blank=True)
    is_featured = models.BooleanField(default=False,blank = True)
    is_converted = models.BooleanField(default=False,blank = True)
    rating = models.DecimalField(max_digits=5, decimal_places=1,default=None,blank = True)
    is_uploaded = models.BooleanField(default=False,blank = True)

    def __str__(self):
        return self.episode_ID


    def get_absolute_url(self):
        return reverse("TV:uploademanualepisode")# after saving a episode where to go
