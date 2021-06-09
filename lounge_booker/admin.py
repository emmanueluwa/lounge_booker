from django.contrib import admin

from .models import BusinessHour, Lounge, Setting, Table, Booking

# Register your models here.
class BusinessHourInline(admin.TabularInline):
    model = BusinessHour
    extra = 1
    show_change_link = True


class TableInline(admin.TabularInline):
    model = Table
    extra = 1
    show_change_link = True


class SettingInline(admin.TabularInline):
    model = Setting
    extra = 1
    show_change_link = True

@admin.register(Lounge)
class LoungeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address1",
        "address2",
        "postcode",
        "created_at",
        "modified_at",
    )
    inlines = (BusinessHourInline, TableInline, SettingInline,)


    def __str__(self):
        return self.name

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "lounge",
        "table",
        "date",
        "created_at",
        "modified_at",
    )

