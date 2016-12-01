from django.shortcuts import render, redirect, get_object_or_404
from tripPlanner.models import *
from django.contrib.auth.decorators import login_required
from tripPlanner.forms import *
from django.db import transaction
import django.contrib.auth.views
from django.http import HttpResponse, Http404
from mimetypes import guess_type
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from datetime import datetime,timedelta
import googlemaps
from django.conf import settings
from tripPlanner.places import places,places_nearby
import json, urllib.request
import copy
import math


# login method
def cus_login(request):
    context = {'register_form': RegistrationForm(), 'from_login': True}
    return django.contrib.auth.views.login(request, template_name="tripPlanner/welcome.html", extra_context=context)

@transaction.atomic
def register(request):
    context = {}

    if request.method == 'GET':
        context['register_form'] = RegistrationForm()
        return render(request, 'tripPlanner/welcome.html', context)

    form = RegistrationForm(request.POST)
    context['register_form'] = form
    if not form.is_valid():
        return render(request, 'tripPlanner/welcome.html', context)
    new_user = User.objects.create_user(username = form.cleaned_data['username'], \
                                        first_name = form.cleaned_data['first_name'], \
                                        last_name = form.cleaned_data['last_name'], \
                                        password = form.cleaned_data['password1'], \
                                        is_active = False)
    new_user.save()

    # generate oken
    token = default_token_generator.make_token(new_user)
    new_profile = Profile.objects.get(user=new_user)
    new_profile.token = token
    new_profile.save()

    # send authentication email
    email_body = """
    Welcome to join tripPlanner!
    Please click the link below to verify your email address and complete the
    registration of your account:
    http://%s%s""" %(request.get_host(), reverse('register_confirm', args=(new_user.username, token)))

    send_mail(subject="Wecome to join tripPlanner", \
              message=email_body, \
              from_email="tripPlanner@gmail.com", \
              recipient_list=[new_user.username])

    # message displayed on browser after registration
    context['message'] = """
    An activation link has been already sent to your email:""" + new_user.username + """.
    Please check your email and click the link to activate your account. Thanks."""

    return render(request, 'tripPlanner/welcome.html', context)

@transaction.atomic
def register_confirm(request, username, token):
    curr_user = get_object_or_404(User, username=username)
    curr_pro = get_object_or_404(Profile, user=curr_user)
    if (token == curr_pro.token):
        # update user and profile
        curr_user.is_active = True
        curr_user.save()
        curr_pro.token=""
        curr_pro.save()
        login(request, curr_user)
        return redirect(reverse('home'))
    else:
        return render(request, 'tripPlanner/welcome.html', {'message': "Wrong Token For Registration!"})

@transaction.atomic
def forget_password(request):
    if request.method == 'GET':
        return render(request, 'tripPlanner/welcome.html', {'title': "Forget Password", 'updated_form': ForgetPasswordForm()})
    form = ForgetPasswordForm(request.POST)
    if not form.is_valid():
        return render(request, 'tripPlanner/welcome.html', {'title': "Forget Password", 'updated_form': ForgetPasswordForm(), 'error': "The email has not been registered."})

    curr_user = get_object_or_404(User, username=form.cleaned_data['username'])
    curr_pro = get_object_or_404(Profile, user=curr_user)
    # generate oken
    token = default_token_generator.make_token(curr_user)
    curr_pro.token = token
    curr_pro.save()

    # send authentication email
    email_body = """
    Your account is trying to reset password. Please click the link below to reset your password.
    http://%s%s""" %(request.get_host(), reverse('password_confirm', args=(curr_user.username, token)))

    send_mail(subject="Reset Password for tripPlanner", \
              message=email_body, \
              from_email="tripPlanner@gmail.com", \
              recipient_list=[curr_user.username])

    # message displayed on browser after registration
    context = {}
    context['message'] = """
    An Password Reset link has been already sent to your email:""" + curr_user.username + """.
    Please check your email and click the link to reset your password. Thanks."""

    return render(request, 'tripPlanner/welcome.html', context)

@transaction.atomic
def password_confirm(request, username, token):
    if not username or not token:
        return render(request, 'tripPlanner/welcom.html', {'message': "Missing username or token!"})
    curr_user = get_object_or_404(User, username=username)
    curr_pro = get_object_or_404(Profile, user=curr_user)
    if (token == curr_pro.token):
        # update user and profile
        curr_pro.token=""
        curr_pro.save()
        return render(request, 'tripPlanner/welcome.html', {'title': "Reset Password", 'updated_form': ModifyPasswordForm(), 'username': curr_user.username})
    else:
        return render(request, 'tripPlanner/welcome.html', {'message': "Wrong Token For Reset Password!"})

@transaction.atomic
def reset_password(request):
    context = {}
    form = ModifyPasswordForm(request.POST)
    context['updated_form'] = form
    context['title'] = "Reset Password"
    if not 'username' in request.POST or not request.POST['username']:
        context['error'] = 'Invalid username'
        return render(request, 'tripPlanner/welcome.html', context)
    context['username'] = request.POST['username']
    if not form.is_valid():
        context['error'] = "Confirmed password and password do not match."
        return render(request, 'tripPlanner/welcome.html', context)

    curr_user = get_object_or_404(User, username=request.POST['username'])
    curr_user.set_password(form.cleaned_data['password1'])
    curr_user.save()
    # authenticate the new user and login the mainstream page
    new_user = authenticate(username=request.POST['username'], \
                            password=request.POST['password1'])
    login(request, new_user)
    return redirect('/')

@login_required
def profile(request):
    destinations = set()
    for trip in Trip.objects.filter(user=request.user):
        destinations.add(trip.destination)
    return render(request, 'tripPlanner/profile.html', {"destinations": destinations})

@login_required
def editProfile(request):
    user_form = UserForm(instance=request.user)
    ProfileInlineFormset = inlineformset_factory(User, Profile, can_delete=False, fields=('photo',), widgets = {'photo': forms.FileInput(attrs={'class': 'form-control'})})
    formset = ProfileInlineFormset(instance=request.user)
    if request.user.is_authenticated():
        if request.method == 'POST':
            user_form = UserForm(request.POST, request.FILES, instance=request.user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)
                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return redirect('/tripPlanner/profile')
        return render(request, 'tripPlanner/editProfile.html', {'noodle': request.user.username, 'noodle_form': user_form, 'formset': formset})
    else:
        raise PermissionDenied

@login_required
def getPhoto(request):
    profile = get_object_or_404(Profile, user=request.user)
    if not profile.photo:
        raise Http404
    content_type = guess_type(profile.photo.name)
    return HttpResponse(profile.photo, content_type=content_type)

def addAttraction(request):
    context={}

    form=AttractionEditForm()
    if request.method == 'GET':
        return render(request,'tripPlanner/addAttractions.html',{'form':form})


    form=AttractionEditForm(request.POST,request.FILES)
    context['form']=form
    if not form.is_valid():
        return render(request,'tripPlanner/addAttractions.html',context)
    attr=form.save()

    context['form']=AttractionEditForm()
    context['attractions']=Attraction.objects.all()
    return render(request,'tripPlanner/addAttractions.html',context)

@login_required
def home(request):
    history_trips = Trip.objects.filter(user=request.user, end_date__lt=datetime.now())
    future_trips = Trip.objects.filter(user=request.user, end_date__gte=datetime.now())
    return render(request, 'tripPlanner/home.html', {"history_trips": history_trips, "future_trips": future_trips})

@login_required
def setTrip(request):
    context={}

    form=TripSettingForm()
    if request.method == 'GET':
        return render(request,'tripPlanner/startTrip.html',{'form':form})

    form=TripSettingForm(request.POST)
    if not form.is_valid():
        return render(request,'tripPlanner/startTrip.html',{'form':form})

    address=Address()
    #create address object
    if not Address.objects.filter(name=form.cleaned_data['destination']).exists():
        address=Address(name=form.cleaned_data['destination'])
        address.save()
    else:
        address=Address.objects.get(name=form.cleaned_data['destination'])


    #create trip object
    trip=Trip(start_date=form.cleaned_data['start_date'],
              end_date=form.cleaned_data['end_date'],
              destination=address,
              origin=form.cleaned_data['origin'],
              user=request.user)
    trip.save()

    #create daytrip object
    startdate=form.cleaned_data['start_date']
    enddate=form.cleaned_data['end_date']

    # daytrip_id_list=[]
    # start_date_trip=DayTrip(date=form.cleaned_data['start_date'],trip=trip)
    # start_date_trip.save()
    # daytrip_id_list.append(start_date_trip.id)

    days_num=int((enddate-startdate).days)

    for n in range(0,days_num+1):
        print(n)
        datestring=(startdate+timedelta(n)).strftime('%Y-%m-%d')
        daytrip=DayTrip(date=datestring,trip=trip)
        daytrip.save()

    return redirect(reverse('showAttractions',args=[trip.id]))

@login_required
def showAttractions(request,tripid):
    trip=get_object_or_404(Trip,id=tripid,user=request.user)
    address=trip.destination
    destination_name=address.name

    #retrieve attractions
    attr_tuple=getAttractions(destination_name)
    attractions=attr_tuple[0]
    name=attr_tuple[1]


    daytrip_id_list=[]
    daytrip_set=DayTrip.objects.filter(trip=trip)
    for daytrip in daytrip_set:
        # daytrip_id_list.append(daytrip.id)
        daytrip_id_list.append(daytrip)

    days_num=int((trip.end_date-trip.start_date).days)

    context={}
    context['destination']=name
    context['attractions']=attractions
    context['tripid']=trip.id
    context['daytrips']=zip(daytrip_id_list,range(1,days_num+2))
    context['days_num']=days_num+1
    context['days_range']=range(1,days_num+2)

    return render(request,'tripPlanner/attractions.html',context)

@transaction.atomic
def getAttractions(destination):
    client=googlemaps.Client(key=settings.GOOGLE_API_KEY)
    address=get_object_or_404(Address,name=destination)
    #if attractions for an address already exist
    if Attraction.objects.filter(address=address).exists():
        attractions=Attraction.objects.filter(address=address).order_by('id')
        return (attractions,destination)
    #for the first time call this function for a specific address
    else:
        place_json=places(client,destination)
        name=""
        attractions=[]
        if place_json['status']=='OK':
            #get addr detail and get image
            name=place_json['results'][0]['name']
            location=str(place_json['results'][0]['geometry']['location']['lat'])+","+str(place_json['results'][0]['geometry']['location']['lng'])
            reference=place_json['results'][0]['photos'][0]['photo_reference']
            description="empty"

            address.name=name
            address.location=location
            address.description=description
            address.image_reference=reference

            address.save()
            #addr.getImage(client=client,reference=reference)
            types=['amusement_park','aquarium','art_gallery','casino','church','movie_theater',
        'museum','night_club','park','place_of_worship','shopping_mall','stadium','zoo']
            attraction_json=places_nearby(location,10000,types,settings.GOOGLE_API_KEY)

            #save attraction object and retrieve images for them
            if attraction_json['status']=='OK':
                for attraction in attraction_json['results']:
                    attr_name=attraction['name']
                    attr_location=str(attraction['geometry']['location']['lat'])+","+str(attraction['geometry']['location']['lng'])
                    if 'photos' in attraction.keys():
                        attr_reference=attraction['photos'][0]['photo_reference']
                    else:
                        continue
                    attr_description=getAttrDescription(attr_name)

                    attr=Attraction(name=attr_name,
                                    address=address,
                                    location=attr_location,
                                    description=attr_description,
                                    image_reference=attr_reference)

                    if 'vicinity' in attraction.keys():
                        attr.formatted_address = attraction['vicinity']
                    if 'rating' in attraction.keys():
                        attr.rating = attraction['rating']
                    if 'price_level' in attraction.keys():
                        attr.price = attraction['price_level']
                    if 'types' in attraction.keys():
                        attr.tag = ", ".join(attraction['types'])

                    attr.save()
                    attractions.append(attr)

        return (attractions,name)

@login_required
def getImage(request,attraction_id):
    client=googlemaps.Client(key=settings.GOOGLE_API_KEY)
    attr=Attraction.objects.get(id=attraction_id)
    if not attr.picture:
        attr.getImage(client=client,reference=attr.image_reference)
    return HttpResponse(attr.picture.url)


@login_required
def get_address_image(request,address_id):
    client=googlemaps.Client(key=settings.GOOGLE_API_KEY)
    addr=Address.objects.get(id=address_id)
    if not addr.picture:
        addr.getImage(client=client,reference=addr.image_reference)
    return HttpResponse(addr.picture.url)

@login_required
@transaction.atomic
def assignAttraction(request):
    if not 'tripid' in request.POST or not request.POST['tripid']:
        raise Http404("The trip does not exist.")

    tripid = request.POST['tripid']
    trip = get_object_or_404(Trip, id=tripid)
    dayTrips = DayTrip.objects.filter(trip=trip)
    print("trip id:",tripid,"daytrip:",dayTrips)

    for dayTrip in dayTrips:
        daytrip_id = "daytrip_" + str(dayTrip.id)
        print(daytrip_id)
        if not daytrip_id in request.POST or not request.POST[daytrip_id]:
            raise Http404("The trip does not exist.")

        attractions = request.POST[daytrip_id]
        # print(attractions)
        if len(attractions) == 1:
            continue

        attractions = attractions[2:]
        attractionsList = attractions.split(",")
        schedule = 0

        for attr in attractionsList:
            attraction = get_object_or_404(Attraction, id=attr)
            new_unit = Unit(schedule=schedule, dayTrip=dayTrip, attraction=attraction)
            new_unit.save()
            schedule = schedule + 1

        if 'detail-action' in request.POST:
            return redirect(reverse("showAttractions", kwargs={"tripid":tripid}))

    return redirect(reverse("optimize", kwargs={"tripid":tripid}))


@login_required
def optimizePath(request, tripid):
    context = {}

    trip = get_object_or_404(Trip, id=tripid)
    dayTrips = DayTrip.objects.filter(trip=trip)
    totalDist = 0

    context['trip'] = trip
    context['dayTrips'] = []
    totalDist = 0

    for dayTrip in dayTrips:
        units = list(Unit.objects.filter(dayTrip=dayTrip))

        locations = findOriginDest(units)
        result = {}
        result['dayTrip'] = dayTrip
        result['locations'] = locations[0]
        result['locatioinids'] = locations[1]
        result['units'] = units
        context['dayTrips'].append(result)

    return render(request,  'tripPlanner/day-optimization.html', context)



def findOriginDest(units):
    if len(units) == 0:
        return ('','')
    elif len(units) == 1:
        return (units[0].attraction.location, units[0].id)
    elif len(units) == 2:
        return (units[0].attraction.location + "|" + units[1].attraction.location, \
                str(units[0].id) + "|" + str(units[1].id))

    points = ''
    pointIds = ''
    for i in list(range(len(units))):
        points += units[i].attraction.location + "|"
        pointIds += str(units[i].id) + "|"
    points = points[:-1]
    pointIds = pointIds[:-1]

    result = getMaxDistance(points, pointIds)
    return result



def getMaxDistance(points, pointIds):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + points + \
                                            "&destinations=" + points + "&mode=DRIVING" + \
                                            "&key=AIzaSyAwACYuRoHRMXtGOxuGNMSlSYm2kKw6_c0"
    data = urllib.request.urlopen(url).read().decode('utf-8')
    result = json.loads(data)
    if result['status'] != 'OK':
        return ''

    maxDist = 0
    furthestPair = [0, 0]
    i = 0
    for row in result['rows']:
        j = 0
        for element in row['elements']:
            dist = element['distance']['value']
            try:
                dist = int(dist)
                if dist > maxDist:
                    maxDist = dist
                    furthestPair = [i, j]
                print(maxDist, dist)
                j += 1
            except:
                j += 1
        i += 1

    points = points.split("|")
    pointIds = pointIds.split("|")

    path = points[furthestPair[0]] + '|'
    pathId = pointIds[furthestPair[0]] + '|'
    for k in list(range(len(points))):
        if k == furthestPair[0] or k == furthestPair[1]:
            continue
        path += points[k] + '|'
        pathId += pointIds[k] + '|'
    path += points[furthestPair[1]]
    pathId += pointIds[furthestPair[1]]
    print(path, pathId)
    return (path, pathId)


@login_required
def savePath(request, tripid):
    print(tripid)
    trip = get_object_or_404(Trip, id=tripid)
    dayTrips = DayTrip.objects.filter(trip=trip)
    for dayTrip in dayTrips:
        route = "route-" + str(dayTrip.id)
        if not route in request.POST or not request.POST[route]:
            raise Http404("The day trip does not exist.")

        optimizedRoute = request.POST[route]
        if optimizedRoute == "#":
            continue

        unitIds = optimizedRoute.split("|")
        schedule = 0
        for unitId in unitIds:
            unit = get_object_or_404(Unit, id=unitId)
            unit.schedule = schedule
            unit.save()
            schedule += 1

    return redirect(reverse("displayTrip", kwargs={"tripid":tripid}))


@login_required
def displayTrip(request, tripid):
    trip = get_object_or_404(Trip, id=tripid)
    dayTrips = DayTrip.objects.filter(trip=trip)

    context = {}
    context['trip'] = trip
    context['dayTrips'] = []

    for dayTrip in dayTrips:
        result = {}
        result['daytrip'] = dayTrip
        result['units'] = list(Unit.objects.filter(dayTrip=dayTrip).order_by('schedule'))
        context['dayTrips'].append(result)

    return render(request, 'tripPlanner/display.html', context)

@login_required
def deleteTrip(request, tripid):
    print("delete", tripid)
    trip = get_object_or_404(Trip, id=tripid)
    trip.delete()

    return redirect(reverse('home'))

def getAttrDescription(name):
    # retrieve attraction obj
    description="Sorry, no description for now."
    try:
        # retrieve attraction info from wiki API
        url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=" + name
        url = url.replace(' ', '%20')
        data = urllib.request.urlopen(url).read().decode('utf-8')

        # parse data
        result = json.loads(data)
        pages = list(result['query']['pages'].values())
        title = pages[0]['title']
        attr_description = pages[0]['extract']
        if len(attr_description)!=0:
            description = attr_description
    except Exception:
        # maintain the default description
        description = "Sorry, no description for now."

    # retrieve first 250 character
    #summary = attr.description.split()[0:100]
    #return ' '.join(summary) + "..."
    return description

# def getAttractionDetail(request, tripid, attraction_id):
#     context = {}
#
#     # get attraction info
#     attr = get_object_or_404(Attraction, id=attraction_id)
#     context['attraction'] = attr
#
#     # get trip details
#     trip=get_object_or_404(Trip,id=tripid,user=request.user)
#
#     daytrip_id_list=[]
#     daytrip_set=DayTrip.objects.filter(trip=trip)
#     for daytrip in daytrip_set:
#         daytrip_id_list.append(daytrip)
#     days_num=int((trip.end_date-trip.start_date).days)
#
#     context['tripid']=trip.id
#     context['daytrips']=zip(daytrip_id_list,range(1,days_num+2))
#     context['days_num']=days_num+1
#     context['days_range']=range(1,days_num+2)
#
#     return render(request, 'tripPlanner/attractionDetail.html', context)

def getAttractionDetail(request, attraction_id):
    # get attraction info
    attr = get_object_or_404(Attraction, id=attraction_id)
    context={}
    context['attraction'] = attr

    return render(request,'tripPlanner/attraction.json',context)
