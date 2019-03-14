from django import forms
from .models import CategoryForTv


class createTVForm(forms.Form):
    TV_id = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'TV_ID'
    }))

    TV_title = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'TV_title'
    }))
    category_id = forms.ModelChoiceField(queryset=CategoryForTv.objects.all())

    year = forms.IntegerField(required=False,min_value=1800,widget=forms.NumberInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Year'
    }))

    TV_timeline = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'TV Timeline'
    }))

    numberOfSeason = forms.IntegerField(required=False,min_value=0,widget=forms.NumberInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Number Of Season'
    }))

    totalEpisode = forms.IntegerField(required=False,min_value=0,widget=forms.NumberInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Total Episode Found'
    }))

    genre = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'Genre'
    }))

    rating = forms.DecimalField(max_digits=5, decimal_places=1,max_value=10.0,required=False,min_value=0.0,widget=forms.NumberInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'rating',
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

    is_featured = forms.BooleanField(required=False)

    API_name = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class' : 'form-control',
        'placeholder' : 'API_name'
    }))
