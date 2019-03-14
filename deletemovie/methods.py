from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
from imdb import IMDb, helpers
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from movies.models import *
from movies.forms import *
import paramiko
import sys
import os
import re
import json
from django.core import serializers
from stat import S_ISDIR
##############################################################



########################### START ACCOUNT AUTHENTICATION SECTION ####################
host = '103.83.15.87'
port = 22
username = 'cyber'
password ='intel12##'

# User Login for Moderators or Admins only
def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # make authentication
        user = authenticate(request, username=username, password=password)

        if user is not None:  # Found Login Credentials in Database
            login(request, user)
            messages.success(request, 'Login Successfull')
            return HttpResponseRedirect(reverse('deletemovie:deleteMovies'), {'user': user})
        else:
            messages.error(request, 'Do I know you? I have no record of your Identity')
            return HttpResponseRedirect(reverse('deletemovie:userlogin'), {'user': user})
    else:
        return render(request, 'accounts/user_login.html')



# Add Movies but requires login authentication
@login_required
def userLogout(request):
    logout(request)
    request.session.flush()
    messages.info(request, 'You have successfully logged out!')
    return redirect('movies:userlogin')


########################### END ACCOUNT AUTHENTICATION SECTION ####################


########################### START SFTP DELETE SECTION ####################

#Check if the path is existing or not
def isdir(sftp, path):
    try:
        return S_ISDIR(sftp.stat(path).st_mode)
    except IOError:
        # print("Path/File is not found in remote directory.")
        return False

def SFTPMovieDIRDelete(sftp, path, remotepath):
    # print("insdie FUck" ,sftp)
    try:
        files = sftp.listdir(path=path)
        for f in files:
            filepath = path + "/" + f
            # print(filepath)
            if isdir(sftp,filepath):
                SFTPMovieDIRDelete(sftp,filepath,remotepath)
                    # print("wa")
            else:
                sftp.remove(filepath)
            sftp.rmdir(remotepath)
        sftp.close()
        # print("Data has been successfully removed!")
        return True
    except:
        # print("Can't connect to the server to DELETE MOVIE")
        return False




########################### END SFTP DELETE SECTION ####################


########################### START RAW METHOD SECTION ####################






########################### END RAW METHOD SECTION ####################
