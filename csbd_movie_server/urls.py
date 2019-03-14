from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from movies import views,methods

urlpatterns = [
    path('',include('movies.urls')),
    path('login/',methods.userLogin, name='userlogin'),
    path('logout/',methods.userLogout),
    path('testing/',include('testing.urls')),
    # path('testing/test/',include('testing.urls')),
    path('add_movies/',views.addMovies, name='addmovies'),
    path('delete_movies/',include('deletemovie.urls')),
    path('TVs/',include('Series.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
