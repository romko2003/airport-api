from django.contrib import admin
from .models import Airport, AirplaneType, Airplane, Route, Crew, Flight, Order, Ticket

admin.site.register([Airport, AirplaneType, Airplane, Route, Crew, Flight, Order, Ticket])
