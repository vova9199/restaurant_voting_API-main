from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView
from rest_framework.versioning import AcceptHeaderVersioning

from .views import (
    RegisterUserAPIView,
    UserLoginAPIView,
    CreateRestaurantAPIView,
    UploadMenuAPIView,
    CreateEmployeeAPIView,
    RestaurantListAPIView,
    CurrentDayMenuList,
    VoteAPIView,
    ResultsAPIView
)

app_name = 'api'


urlpatterns = [
    path(
        'registration/',
        RegisterUserAPIView.as_view(),
        name="registration", ),
    path(
        'login/',
        UserLoginAPIView.as_view(),
        name="login"),
    path(
        'create_restaurant/',
        CreateRestaurantAPIView.as_view(),
        name="create-restaurant"),
    path(
        'upload_menu/',
        UploadMenuAPIView.as_view(),
        name="upload-menu"),
    path(
        'create_employee/',
        CreateEmployeeAPIView.as_view(),
        name="create-employee"),
    path(
        'restaurants/',
        RestaurantListAPIView.as_view(),
        name="restaurants"),
    path(
        'menu_list/',
        CurrentDayMenuList.as_view(),
        name="menu-list"),
    path(
        'vote/<int:menu_id>/',
        VoteAPIView.as_view(),
        name="new-vote"),
    path(
        'results/',
        ResultsAPIView.as_view(),
        name="results"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
