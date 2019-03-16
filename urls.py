from django.contrib import admin
from django.urls import path
from software import views,methods

app_name='software'

urlpatterns = [
    path('login/',views.userLogin, name='userlogin'),
    path('logout/',views.userLogout, name='userlogout'),
    path('delete_software/',views.deleteSoftware, name='deletesoftware'),
    path('add_software/',views.addSoftware, name='addsoftware'),
    path('update_software/',views.updateSoftware, name='updatesoftware'),
]
