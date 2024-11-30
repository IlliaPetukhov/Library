from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from library_borrow.views import (

)

router = routers.DefaultRouter()
app_name = "library-api-1"
