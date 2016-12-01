from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from tripPlanner.places import places_photo
import os
from django.core.files import File

#data model for Profile
class Profile(models.Model):
    user = models.OneToOneField(User, \
                                on_delete=models.CASCADE, \
                                primary_key=True)
    photo = models.ImageField(upload_to="Profile_photo/", blank=True)
    token = models.CharField(max_length=500, blank=True)

def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        profile = Profile(user=user, photo="", token="")
        profile.save()
post_save.connect(create_profile, sender=User)

# data model for address
class Address(models.Model):
    name = models.CharField(max_length=200)
    picture = models.ImageField(upload_to="Address_photo/", blank=True)
    description = models.CharField(max_length=500,default="")
    location = models.CharField(max_length=200,default='40.440624,-79.995888')
    image_reference=models.CharField(max_length=500)

    def getImage(self, client, reference=''):
        if reference != '' and client: # Don't do anything if we don't get passed anything!
            image = places_photo(client,reference,400,400) # See function definition below
            #save the file to path
            f = open(self.name, 'wb')
            for chunk in image:
                if chunk:
                    f.write(chunk)
            f.close()
            #save it to image field
            self.picture.save(
                os.path.basename(self.name),
                File(open(self.name,'rb'))
            )
            #self.save()


#data model for spot sight
class Attraction(models.Model):
    name = models.CharField(max_length=200, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    location=models.CharField(max_length=200, default='40.440624,-79.995888')
    picture = models.ImageField(upload_to="Attraction_photo/", blank=True)
    description = models.CharField(max_length=500)
    image_reference = models.CharField(max_length=500)
    formatted_address = models.CharField(max_length=200, default='None')
    rating = models.CharField(max_length=5, default='None')
    price = models.CharField(max_length=5, default='None')
    tag = models.CharField(max_length=200, default='None')

    def getImage(self, client, reference=''):
        if reference != '' and client: # Don't do anything if we don't get passed anything!
            image = places_photo(client,reference,400,400) # See function definition below
            #save the file to path
            f = open(self.name, 'wb')
            for chunk in image:
                if chunk:
                    f.write(chunk)
            f.close()
            self.picture.save(
                os.path.basename(self.name),
                File(open(self.name,'rb'))
            )
            self.save()


    @property
    def html(self):
        html="<div class='row'>\
  <div class='col-md-3'>\
     <a class='thumbnail'>\
        <img src='%s' alt='%s'>\
        <p class='hidden_attraction_id'>%s</p>\
     </a>\
  </div>\
  <div class='col-md-9 leftalign'>\
     <p>Rating: %s</p>\
     <p>Price Level: %s</p>\
     <p>Address: %s</p>\
     <p>Tag: %s</p>\
     <p>Description: %s </p>\
  </div>\
</div>\
" %(self.picture.url,self.name,self.id,self.rating,self.price,self.formatted_address,self.tag,self.description)

        return html

#data model for trip
class Trip(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    destination = models.ForeignKey(Address,on_delete=models.CASCADE)
    origin = models.CharField(max_length=200)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

# data model for DayTrip
class DayTrip(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    date = models.DateField()

#data model for a unit inside a trip
class Unit(models.Model):
    schedule = models.IntegerField(null=True) # sequence to visit attraction within a day
    dayTrip = models.ForeignKey(DayTrip, on_delete=models.CASCADE, null=True)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)

    class Meta:
        ordering = ('schedule',)
