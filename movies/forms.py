from django import forms
from . models import Category


class addMovieForm(forms.Form):
    movie_id = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Movie_ID'
    }))

    movie_title = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'movie_title'
    }))

    

    year = forms.IntegerField(required=False,min_value=1800,widget=forms.NumberInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Year'
    }))

    genre = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Genre'
    }))

    IMDB_rating = forms.DecimalField(max_digits=5, decimal_places=1,max_value=10.0,required=False,min_value=0.0,widget=forms.NumberInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'IMDB_rating',
    }))

    director = forms.CharField(required=False,widget=forms.TextInput(attrs={
         'class' : 'form-control',
         'placeholder' : 'Director',
     }))

    writer = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Writers'
    }))

    cast = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Casts'
    }))
    plot = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Plot'
    }))

    poster_path = forms.ImageField(required=False,widget=forms.ClearableFileInput(attrs={
    }))

    destination_location = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder': 'Destination location generates with API'
    }))

    source_location = forms.FileField(required=False,widget=forms.ClearableFileInput(attrs={
        'placeholder' : 'Store Path'
    }))

    is_featured = forms.BooleanField(required=False)
    is_converted = forms.BooleanField(required=False)

    API_name = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'API_name'
    }))
