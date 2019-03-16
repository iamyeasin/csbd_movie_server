from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse,JsonResponse,HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from . models import UploadSoftware
from settings.models import *
from . models import *
from . forms import *
import paramiko,sys,os,re,json
from django.core import serializers
import datetime
from time import gmtime, strftime

##############################################################

### Add / Delete Software Method section

########################### START ACCOUNT AUTHENTICATION SECTION ####################
host =  FTPDetails.objects.get(pk=1).server_address
port = FTPDetails.objects.get(pk=1).portnumber
username = FTPDetails.objects.get(pk=1).username
password = FTPDetails.objects.get(pk=1).password



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
            return HttpResponseRedirect(reverse('software:addsoftware'), {'user': user})
        else:
            messages.error(request, 'Do I know you? I have no record of your Identity')
            return HttpResponseRedirect(reverse('software:userlogin'), {'user': user})
    else:
        return render(request, 'accounts/user_login.html')



# Add Software but requires login authentication
@login_required
def userLogout(request):
    logout(request)
    request.session.flush()
    return redirect('software:userlogin')


########################### END ACCOUNT AUTHENTICATION SECTION ####################





######################### SAVE SOFTWARE INFORMATION #########################

def saveSoftwareInformation(request):
    try:
        software_ID = request.POST.get('software_id')
        software_TITLE = request.POST.get('software_title')
        software_FILE_SIZE = request.POST.get('software_file_size')
        destination_LOCATION = request.POST.get('destination_location')
        manual_IMAGE = request.FILES.get('image_file')
        file_NAME = request.POST.get('file_name')
        filePath = os.path.join( destination_LOCATION, file_NAME )

        uploadInfo = UploadSoftware(
            software_id = software_ID,
            software_title = software_TITLE,
            destination_path = destination_LOCATION,
            software_file_size = software_FILE_SIZE,
            poster_path = manual_IMAGE,
            file_path = filePath,
        )

        # print("asdf")
        posterlocation = destination_LOCATION + "/poster"
        npath = posterlocation + "/" +  slugify(software_TITLE) +  '.' + 'jpg';

        uploadInfo.save()
        # print("bal")

        if not os.path.exists( posterlocation ):
           os.makedirs( posterlocation )

        # img_data = requests.get(manual_IMAGE).content
        # print(x)
        # with open( npath, 'wb') as handler:
            # handler.write( img_data )

        uploadInfo.save()
        print("SOFTWARE SAVED")
        return "OK"

    except:
        return "EROR"



################## GENERATE MANUAL PRIMARY KEY ##############

def generatePrimaryKey():
    currentTime = strftime("%Y%m%d%H%M%S",gmtime())
    key= "SID#" + currentTime

    idExists = UploadSoftware.objects.filter(software_id=key).count()

    if idExists == 0:
        return key

    else:
        while idExists == 0:
            currentTime = strftime("%Y%m%d%H%M%S",gmtime())
            key = "SID#" + currentTime
            idExists = UploadSoftware.objects.filter(software_id=key).count()
            return key
