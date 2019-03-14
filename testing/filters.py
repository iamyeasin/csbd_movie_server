import django_filters
from movies.models import UploadMovie,Category

class MovieFilter(django_filters.FilterSet):

    class Meta:
        model = UploadMovie
        fields = {
            'movie_id' : ['icontains'],
            'movie_title':['icontains'],
            'API_name': ['icontains'],
            'year' : ['icontains'],

        }
