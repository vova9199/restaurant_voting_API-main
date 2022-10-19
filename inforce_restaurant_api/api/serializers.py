from rest_framework import serializers
from .models import User, Employee, Menu, Restaurant


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User

        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "password",
            "username",
        ]


class UserLoginSerializer(serializers.Serializer):
    token = serializers.CharField(allow_blank=True, read_only=True)
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = [
            'email',
            'password',
        ]
        read_only_fields = ('id',)


class CreateRestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        fields = [
            'name',
            'contact_no',
            'address',
        ]
        model = Restaurant


class UploadMenuSerializer(serializers.ModelSerializer):

    def create(self, validated_data):

        menu = Menu(
            file=validated_data['file'],
            restaurant=validated_data['restaurant'],
            uploaded_by=validated_data['uploaded_by']
        )
        menu.save()
        return menu

    class Meta:
        fields = [
            'restaurant',
            'file',
            'uploaded_by'

        ]
        model = Menu


class EmployeeSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    employee_no = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            "username",
            'employee_no'

        ]


class RestaurantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class MenuListSerializer(serializers.ModelSerializer):

    restaurant = serializers.CharField(read_only=True)

    class Meta:
        model = Menu
        fields = '__all__'


class ResultMenuListSerializer(serializers.ModelSerializer):

    restaurant = serializers.CharField(read_only=True)

    class Meta:
        model = Menu
        fields = [
            'id',
            'file',
            'restaurant',
            'votes',
            'created_at'
        ]
