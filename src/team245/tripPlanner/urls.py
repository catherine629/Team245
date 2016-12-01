from django.conf.urls import include, url

import django.contrib.auth.views
from tripPlanner import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^login$', views.cus_login, name='login'),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^registerConfirm/(?P<username>.*)/(?P<token>.*)$', views.register_confirm, name='register_confirm'),
    url(r'^forgetPassword$', views.forget_password, name="Forget Password"),
    url(r'^passwordConfirm/(?P<username>.*)/(?P<token>.*)$', views.password_confirm, name='password_confirm'),
    url(r'^resetPassword$', views.reset_password, name="Reset Password"),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^editProfile$', views.editProfile, name='editProfile'),
    url(r'^photo$', views.getPhoto, name='photo'),
    url(r'^tripsetting$',views.setTrip,name='setTrip'),
    url(r'^addAttractions$',views.addAttraction,name='addAttractions'),
    url(r'^getAttractionDetail/(?P<attraction_id>\d+)$', views.getAttractionDetail, name="getAttractionDetail"),
    url(r'^assignAttraction$', views.assignAttraction, name='assignAttraction'),
    url(r'^displayTrip/(?P<tripid>\d+)$', views.displayTrip, name="displayTrip"),
    url(r'^optimizePath/(?P<tripid>\d+)$', views.optimizePath, name="optimize"),
    url(r'^savePath/(?P<tripid>\d+)$', views.savePath, name="save"),
    url(r'^deleteTrip/(?P<tripid>\d+)$', views.deleteTrip, name="delete"),
    url(r'^get_image/(?P<attraction_id>\d+)$',views.getImage),
    url(r'^get_address_image/(?P<address_id>\d+)$',views.get_address_image),
    url(r'^show_attraction/(?P<tripid>\d+)$',views.showAttractions,name="showAttractions"),
]
