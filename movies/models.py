from django.db import models
from django.template.defaultfilters import slugify

#Gives a specific path
def upload_location(instance, filename):
    # newname = filename.split('.')[-1]
    # filename = "%s_%s.%s" % (instance.movie_id, instance.movie_title, newname)
    path = ((instance.category_id.initial_path) + "/" + str(instance.year) + "/" +
            slugify(instance.movie_title) + " " + str(instance.year) + "/poster/" + slugify(filename))

    return path


#Category models
class Category(models.Model):
    category_name = models.CharField(max_length=250)
    initial_path = models.CharField(max_length=250)
    background_image = models.FileField(upload_to=upload_location,max_length=700,blank=True)
    frontpage_feature = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name


class UploadMovie(models.Model):
    movie_id = models.CharField(max_length=20, primary_key=True)
    category_id = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    movie_title = models.CharField(max_length=7024)
    year = models.PositiveIntegerField()
    genre = models.CharField(max_length=7024)
    IMDB_rating = models.DecimalField(max_digits=5, decimal_places=1)
    director = models.CharField(max_length=7024)
    writer = models.CharField(max_length=7024)
    cast = models.CharField(max_length=7024)
    plot = models.CharField(max_length=6600)
    poster_path = models.FileField(upload_to=upload_location,max_length=700)
    destination_location = models.CharField(max_length=7024)
    is_featured = models.BooleanField(default=False)
    is_converted = models.BooleanField(default=False)
    API_name = models.CharField(max_length=20)

    def __str__(self):
        return self.movie_title



class MainFeatureHead(models.Model):
    movie_id = models.ForeignKey(UploadMovie, on_delete=models.DO_NOTHING)
    background_poster = models.FileField(upload_to=upload_location,max_length=700)

    def __str__(self):
        return self.username
