from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from api.models import User, Restaurant, Menu, Employee, Vote
from api.token import get_token


class TestRegisterUserAPI(APITestCase):
    def test_post_request_can_register_new_user(self):
        data = {
            "email": "vova9199test@ukr.net",
            "first_name": "Volodymyr",
            "last_name": "Potapenko",
            "phone": "+380977544577",
            "username": "vova_test",
            "password": "testpass"
        }
        self.client.post(reverse("api:registration"), data=data)
        self.assertEqual(User.objects.count(), 1)


class TestLoginClientAPI(APITestCase):
    def test_post_request_can_login_user(self):
        user = User.objects.create(
            first_name='Volodymyr',
            last_name='Potapenko',
            email='vova9199@ukr.net'
        )

        user.set_password('testpass')
        user.save()
        data = {
            "email": "vova9199@ukr.net",
            "password": "testpass"

        }
        res = self.client.post(reverse("api:login"), data=data)
        status = res.json().get('success')
        self.assertEqual(status, True)


class TestCreateRestaurantAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
        self.token = get_token(self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token["access"])

    def test_post_request_can_create_new_restaurant(self):
        data = {
            "name": "Puzata hata",
            "contact_no": "+38097777777",
            "address": "Lviv"

        }
        res = self.client.post(reverse("api:create-restaurant"), data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_post_request_create_new_restaurant_unauthenticated(self):
        self.client.force_authenticate(user=None)
        data = {
            "name": "Puzata chata",
            "contact_no": "+38097777777",
            "address": "Lviv"

        }
        res = self.client.post(reverse("api:create-restaurant"), data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestCreateUploadMenuAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
        self.token = get_token(self.user)
        self.api_authentication()

        self.restaurant = Restaurant.objects.create(name='Burger King', contact_no='+3809777777', address='Lviv')

        self.file = SimpleUploadedFile("file.txt", b"abc", content_type="text/plain")
        self.payload = {"file": self.file, 'restaurant': self.restaurant.id, "uploaded_by": "Volodymyr"}

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token["access"])

    def test_post_request_can_upload_menu(self):
        res = self.client.post(reverse("api:upload-menu"), data=self.payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_post_request_upload_menu_unauthenticated(self):
        self.client.force_authenticate(user=None)

        res = self.client.post(reverse("api:upload-menu"), data=self.payload, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestCreateEmployeeAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
        self.token = get_token(self.user)
        self.api_authentication()

        self.payload = {
            "email": "vova9199@ukr.net",
            "first_name": "Volodymyr",
            "last_name": "Potapenko",
            "phone": "+3809777777",
            "employee_no": "007",
            "username": "Good_boy"

        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token["access"])

    def test_post_request_can_create_new_employee(self):
        res = self.client.post(reverse("api:create-employee"), data=self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_post_request_create_new_employee_unauthenticated(self):
        self.client.force_authenticate(user=None)

        res = self.client.post(reverse("api:create-employee"), data=self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestGetRestaurantsAPI(APITestCase):

    def setUp(self):
        self.restaurant = Restaurant.objects.create(name='Burger King', contact_no='+380212132', address='Kyiv')

    def test_get_request_all_restaurants(self):
        res = self.client.get(reverse("api:restaurants"))
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestGetCurrentDayMenuListAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')

        self.restaurant = Restaurant.objects.create(name='Burger King', contact_no='+3809777777', address='Lviv')

        self.file = SimpleUploadedFile("file.txt", b"abc", content_type="text/plain")

        self.menu = Menu.objects.create(restaurant=self.restaurant, file=self.file, uploaded_by=self.user.username)

    def test_get_request_all_current_day_menu_list(self):
        res = self.client.get(reverse("api:menu-list"))
        self.assertEqual(Menu.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestVoteMenuAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')
        self.employee = Employee.objects.create(user=self.user, employee_no="007")
        self.token = get_token(self.user)
        self.api_authentication()

        self.restaurant = Restaurant.objects.create(name='Burger King', contact_no='+3809777777', address='Lviv')

        self.file = SimpleUploadedFile("file.txt", b"abc", content_type="text/plain")

        self.menu = Menu.objects.create(restaurant=self.restaurant, file=self.file, uploaded_by=self.user.username)

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token["access"])

    def test_get_request_employee_can_vote(self):
        res = self.client.get(reverse("api:new-vote", kwargs={'menu_id': self.menu.id}))

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestGetResultsAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin123')

        self.restaurant = Restaurant.objects.create(name='Burger King', contact_no='+3809777777', address='Lviv')

        self.file = SimpleUploadedFile("file.txt", b"abc", content_type="text/plain")

        self.menu = Menu.objects.create(restaurant=self.restaurant, file=self.file, uploaded_by=self.user.username)

    def test_get_result_of_current_day(self):
        res = self.client.get(reverse("api:results"))
        self.assertEqual(Menu.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


