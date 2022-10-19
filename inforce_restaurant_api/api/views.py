from .token import get_token
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from .models import User, Employee, Restaurant, Menu, Vote
from .serializers import UserSerializer, UserLoginSerializer, CreateRestaurantSerializer, \
    UploadMenuSerializer, EmployeeSerializer, RestaurantListSerializer, MenuListSerializer, ResultMenuListSerializer

today_date = settings.CURRENT_DATE.date()


class RegisterUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()


class UserLoginAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        try:
            user = User.objects.get(email=email)
            fullname = user.first_name + " " + user.last_name
            if check_password(password, user.password):
                jwt_token = get_token(user)
                jwt_access_token = jwt_token["access"]
                jwt_refresh_token = jwt_token["refresh"]
                data = {
                    "msg": "Login success",
                    "success": True,
                    "data": {
                        "name": fullname,
                        "id": user.id,
                        "access_token": jwt_access_token,
                        "refresh_token": jwt_refresh_token}
                }
                return Response(data=data, status=status.HTTP_202_ACCEPTED)
            else:
                res = {
                    "msg": "Invalid login credentials",
                    "data": None,
                    "success": False}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res = {"msg": str(e), "success": False, "data": None}
            return Response(data=res, status=status.HTTP_200_OK)


class CreateRestaurantAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateRestaurantSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UploadMenuAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        try:
            req = request.data
            menu = Menu.objects.filter(restaurant=req.get('restaurant'), created_at__date=settings.CURRENT_DATE)
            if menu.exists():
                res = {
                    "msg": "Menu already added.",
                    "success": False,
                    "data": None}
                return Response(data=res, status=status.HTTP_200_OK)
            serializer = UploadMenuSerializer(data=req)
            if serializer.is_valid():
                serializer.save()
                res = {
                    "msg": "Menu successful uploaded",
                    "success": True,
                    "data": serializer.data}
                return Response(data=res, status=status.HTTP_201_CREATED)

            res = {
                "msg": str(
                    serializer.errors),
                "success": False,
                "data": None}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res = {"msg": str(e), "success": False, "data": None}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)


class CreateEmployeeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        req = request.data

        user = request.user.username
        employee_no = req.get('employee_no')
        employee = Employee.objects.filter(
            Q(employee_no=employee_no)
        )
        text = f"EMPLOYEE NO {employee_no} already exists"
        if employee.exists():
            res = {
                "msg": text,
                "data": None,
                "success": False}
            return Response(data=res, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmployeeSerializer(data=req)

        if serializer.is_valid():
            try:
                new_user = User.objects.create(
                    email=req.get('email'),
                    first_name=req.get('first_name').capitalize(),
                    last_name=req.get('last_name').capitalize(),
                    username=req.get('username'),
                    is_active=True,
                    phone=req.get('phone'),
                    is_staff=True,
                    created_by=user

                )

                password = req.get("password")
                new_user.set_password(password)
                new_user.save()

                Employee.objects.create(
                    user=new_user,
                    employee_no=req.get('employee_no'),
                    created_by=user
                )

                serializer = UserSerializer(new_user)

                es = {
                    "msg": f"Employee successfully created.{employee_no}",
                    "data": serializer.data,
                    "success": True}
                return Response(data=es, status=status.HTTP_201_CREATED)
            except Exception as e:
                res = {"msg": str(e), "data": None, "success": False}
                return Response(data=res, status=status.HTTP_400_BAD_REQUEST)
        res = {"msg": str(serializer.errors), "data": None, "success": False}
        return Response(data=res, status=status.HTTP_400_BAD_REQUEST)


class RestaurantListAPIView(generics.ListAPIView):
    serializer_class = RestaurantListSerializer
    queryset = Restaurant.objects.all()


class CurrentDayMenuList(APIView):

    def get(self, request):
        query = Menu.objects.filter(Q(created_at__date=today_date))
        serializer = MenuListSerializer(query, many=True)
        res = {"msg": 'success', "data": serializer.data, "success": True}
        return Response(data=res, status=status.HTTP_200_OK)


class VoteAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, menu_id):
        username = request.user.username

        employee = Employee.objects.get(user__username=username)
        menu = Menu.objects.get(id=menu_id)

        if Vote.objects.filter(
                employee__user__username=username,
                voted_at__date=today_date,
                menu__id=menu_id).exists():
            res = {"msg": 'You already voted!', "data": None, "success": False}
            return Response(data=res, status=status.HTTP_200_OK)
        else:
            new_vote = Vote.objects.create(
                employee=employee,
                menu=menu

            )
            new_vote.save()
            menu.votes += 1
            menu.save()
            res = {
                "msg": 'You voted successfully!',
                "data": f"You voted for the restaurant with the number {menu_id}",
                "success": True}
            return Response(data=res, status=status.HTTP_200_OK)


class ResultsAPIView(APIView):

    def get(self, request):
        today = settings.CURRENT_DATE
        current_menu_qs = Menu.objects.filter(
            Q(created_at__date=today)).order_by('-votes').first()
        if not current_menu_qs:
            res = {
                "msg": 'Results not found! no menus found for today.',
                "data": None,
                "success": False}
            return Response(data=res, status=status.HTTP_200_OK)
        serializer = ResultMenuListSerializer(current_menu_qs)
        data = {
            "msg": 'The restaurant chosen for today.',
            "data": serializer.data,
            "success": True
        }
        return Response(data=data, status=status.HTTP_200_OK)
