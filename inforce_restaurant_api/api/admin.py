from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'created_at',
        'created_by'
    )


class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'address',
        'created_at',
        'created_by'
    )


class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'restaurant',
        'file',
        'votes',
        'created_at'
    )


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'menu', 'voted_at')


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Vote, VoteAdmin)
