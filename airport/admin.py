from django.contrib import admin

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    search_fields = ("name", "closest_big_city")
    list_display = ("id", "name", "closest_big_city")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "distance")
    list_filter = ("source", "destination")
    search_fields = ("source__name", "destination__name")


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "airplane_type", "rows", "seats_in_row", "capacity")
    list_filter = ("airplane_type",)
    search_fields = ("name",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "airplane", "departure_time", "arrival_time")
    list_filter = ("route__source", "route__destination", "airplane")
    search_fields = ("route__source__name", "route__destination__name")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    search_fields = ("user__email", "user__username")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "flight", "order", "row", "seat")
    list_filter = ("flight",)
