from django.conf.urls import url

from . import views

urlpatterns = [
    # Mumble service control
    url(r'^activate_mumble/$', views.activate_mumble, name='auth_activate_mumble'),
    url(r'^deactivate_mumble/$', views.deactivate_mumble, name='auth_deactivate_mumble'),
    url(r'^reset_mumble_password/$', views.reset_mumble_password,
        name='auth_reset_mumble_password'),
    url(r'^set_mumble_password/$', views.set_mumble_password, name='auth_set_mumble_password'),
]
