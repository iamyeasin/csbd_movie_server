from django.db import models

class FTPDetails(models.Model):
    server_address = models.CharField(max_length=40,blank=False)
    username = models.CharField(max_length=40,blank=False)
    password = models.CharField(max_length=40,blank=False)
    portnumber = models.CharField(max_length=40,blank=False)

    def __str__(self):
        return self.server_address


class TMDBAPIDetails(models.Model):
    username = models.CharField(max_length=30,blank=False)
    password = models.CharField(max_length=30,blank=False)
    API_KEY = models.CharField(max_length=300,blank=False)
    BaseImageLink = models.CharField(max_length=300,blank=False)
    MoviePageLink = models.CharField(max_length=300,blank=False)

    def __str__(self):
        return self.username


class OMDBAPIDetails(models.Model):
    username = models.CharField(max_length=30,blank=False)
    password = models.CharField(max_length=30,blank=False)
    API_KEY = models.CharField(max_length=300,blank=False)
    MoviePageLink = models.CharField(max_length=300,blank=True)

    def __str__(self):
        return self.username


class IMDBAPIDetails(models.Model):
    MoviePageLink = models.CharField(max_length=300,blank=False)

    def __str__(self):
        return self.MoviePageLink
