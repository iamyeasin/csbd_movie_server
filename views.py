from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect,HttpResponseNotFound, Http404, HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.conf import settings
import re, datetime
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from . models import *
from . forms import *
from . import methods
import json,re,os,sys
from django.views.generic import TemplateView,ListView,CreateView,DeleteView
from django.core import serializers
from django.core.files.base import ContentFile
from django.template.defaultfilters import slugify
from . models import *
from . forms import addSoftwareForm
from movies.models import *


##### Base File #####

def index(request):
    print("host",host)
    return render(request, 'base.html')


def addSoftwareLogin(request):
    if request.user.is_authenticated:
        form = addSoftwareForm()
        return render(request,'software/add_software.html',{'form':form})
    else:
        return redirect('software:userlogin')



##### User Login for Moderators or Admins only #######

def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username, password=password) #make authentication

        if user is not  None:  # Found Login Credentials in Database
            login(request,user)
            messages.success(request, 'Login Successfull')
            return HttpResponseRedirect(reverse('software:addsoftware'),{'user':user})

        else:
            messages.error(request, 'Do I know you? I have no record of your Identity')
            return HttpResponseRedirect(reverse('software:userlogin'),{'user':user})

    else:
        return render(request,'accounts/user_login.html')



###### Add software but requires login authentication #####
@login_required
def userLogout(request):
    logout(request)
    request.session.flush()
    return redirect('software:userlogin')

@login_required
def addSoftware(request):
    #If the user is logged in then let him enter the page
    if request.method == 'POST':

        title = request.POST.get('software_title')
        ID = request.POST.get('software_id')
        btnpressed = request.POST.get('btnclicked')


        #  write code to send data to FTP server



       #################  TEST DATA  #################

        # for x,y in request.FILES.items():
        #     print(x,y)

        # for x,y in request.POST.items():
        #             print(x,y)
        ##############################################



        if btnpressed == "upload_software" and ID and title :

            status = methods.saveSoftwareInformation(request)
            print(status)
            if status == "OK":
                return HttpResponse("ok")

            else:
                return HttpResponseNotFound("EROR")

    else:
        if request.user.is_authenticated:
            path = InitialPath.objects.get(pk=1)
            path = path.initial_path
            getID = methods.generatePrimaryKey()
            form = addSoftwareForm() #just pass the form as a context

            return render(request,'software/add_software.html',{'form':form,
                                                            'SID' : getID, 'Dlocation': path   })
        else:
            return redirect('software:userlogin')




 ###########################  Delete Section start #################################

@login_required
def deleteSoftware(request):

    #########  Data fetch from model  #########

    btn = request.POST.get('delete')
    btnpressed = request.POST.get('search')
    if request.method == 'POST' and request.user.is_authenticated:

        form = addSoftwareForm(request.POST, request.FILES)
        title = request.POST.get('software_title')
        ID = request.POST.get('software_id')
        Size = request.POST.get('software_file_size')
        if ID:
            ID = ID.lstrip()
            ID = ID.rstrip()
        else:
            ID = ""


        if btnpressed == "Search":
            # print("ko")
            try:
                if len(ID) > 0:
                    software_info = UploadSoftware.objects.get(software_id=ID)
                else:
                    software_info = UploadSoftware.objects.get(software_title=title)

                destination_location = software_info.destination_path

                if software_info:
                    form_INFO = addSoftwareForm(initial={
                        'software_title': software_info.software_title,
                        'software_id': software_info.software_id,
                        'software_file_size': software_info.software_file_size,
                    })

                    messages.success(request,"Desired data is found on the database")
                    return render(request, 'software/delete_software.html', {'dict': form_INFO,
                                            'destination':destination_location })

            except:
                messages.error(request,"No data Found in the database")
                return render(request, 'software/delete_software.html', {'form': form, })


        ########## bring the data here responds ajax request ############

        # elif btn == "Delete":
        #     # for x,y in request.POST.items():
        #     #     print(x,y)
        #     # ID= request.POST.get('software_id')
        #     print(ID)
        #     instance = UploadSoftware.objects.get(software_id=ID)


        #     return HttpResponse("ok")




    else:
        if request.user.is_authenticated:
            form = addSoftwareForm() #just pass the form as a context

            return render(request,'software/delete_software.html',{'form': form, })
        else:
            return redirect('software:userlogin')



    ###########  Delete fetched data  ############



###########################  Update Section start #################################

@login_required
def updateSoftware(request):

    btn = request.POST.get('delete')
    btnpressed = request.POST.get('search')
    if request.method == 'POST' and request.user.is_authenticated:

        form = addSoftwareForm(request.POST, request.FILES)
        title = request.POST.get('software_title')
        ID = request.POST.get('software_id')
        Size = request.POST.get('software_file_size')
        if ID:
            ID = ID.lstrip()
            ID = ID.rstrip()
        else:
            ID = ""


        if btnpressed == "Search":
            # print("ko")
            try:
                if len(ID) > 0:
                    software_info = UploadSoftware.objects.get(software_id=ID)
                else:
                    software_info = UploadSoftware.objects.get(software_title=title)

                destination_location = software_info.destination_path

                if software_info:
                    form_INFO = addSoftwareForm(initial={
                        'software_title': software_info.software_title,
                        'software_id': software_info.software_id,
                        'software_file_size': software_info.software_file_size,
                    })

                    messages.success(request,"Desired data is found on the database")
                    return render(request, 'software/update_software.html', {'dict': form_INFO,
                                            'destination':destination_location })

            except:
                messages.error(request,"No data Found in the database")
                return render(request, 'software/update_software.html', {'form': form, })

    else:
        if request.user.is_authenticated:
            form = addSoftwareForm() #just pass the form as a context

            return render(request,'software/update_software.html',{'form': form, })
        else:
            return redirect('software:userlogin')
