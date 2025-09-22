from django.db import transaction
from rest_framework import serializers
from .models import (
    Airport, AirplaneType, Airplane, Route, Crew, Flight, Order, Ticket
)

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneListSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirplaneSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True, source="capacity")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneListSerializer(read_only=True)
    available_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time",
            "available_tickets",
        )


class FlightSerializer(serializers.ModelSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    available_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crew",
            "available_tickets",
        )


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("flight", "row", "seat")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "flight", "row", "seat")


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")
        read_only_fields = ("id", "created_at")

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        tickets_data = validated_data.pop("tickets", [])
        order = Order.objects.create(user=user)

        for t in tickets_data:
            flight = t["flight"]
            row, seat = t["row"], t["seat"]
            rows = flight.airplane.rows
            seats_in_row = flight.airplane.seats_in_row

            if not (1 <= row <= rows) or not (1 <= seat <= seats_in_row):
                raise serializers.ValidationError(
                    f"Seat ({row},{seat}) is out of airplane bounds {rows}x{seats_in_row}"
                )

            if Ticket.objects.filter(flight=flight, row=row, seat=seat).exists():
                raise serializers.ValidationError(f"Seat ({row},{seat}) already taken")

            Ticket.objects.create(order=order, flight=flight, row=row, seat=seat)

        return order
