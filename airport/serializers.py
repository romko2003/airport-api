from rest_framework import serializers

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
from airport.services import create_order_with_tickets, SeatBookingError


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)

    source_id = serializers.PrimaryKeyRelatedField(
        source="source",
        queryset=Airport.objects.all(),
        write_only=True,
    )
    destination_id = serializers.PrimaryKeyRelatedField(
        source="destination",
        queryset=Airport.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "source_id",
            "destination_id",
            "distance",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)
    airplane_type_id = serializers.PrimaryKeyRelatedField(
        source="airplane_type",
        queryset=AirplaneType.objects.all(),
        write_only=True,
    )
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "airplane_type_id",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)

    crew = CrewSerializer(many=True, read_only=True)
    crew_ids = serializers.PrimaryKeyRelatedField(
        source="crew",
        many=True,
        queryset=Crew.objects.all(),
        write_only=True,
        required=False,
    )

    route_id = serializers.PrimaryKeyRelatedField(
        source="route",
        queryset=Route.objects.all(),
        write_only=True,
    )
    airplane_id = serializers.PrimaryKeyRelatedField(
        source="airplane",
        queryset=Airplane.objects.all(),
        write_only=True,
    )

    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "route_id",
            "airplane",
            "airplane_id",
            "crew",
            "crew_ids",
            "departure_time",
            "arrival_time",
            "taken_seats",
        )

    def get_taken_seats(self, obj: Flight) -> int:
        return obj.tickets.count()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")
        # order is implicit via parent (Order)
        read_only_fields = ("flight",)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")
        read_only_fields = ("created_at",)


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Creates an order and books seats for a specific flight.
    """
    flight_id = serializers.PrimaryKeyRelatedField(
        queryset=Flight.objects.all(),
        write_only=True,
    )
    seats = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        allow_empty=False,
        write_only=True,
    )
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "created_at", "flight_id", "seats", "tickets")
        read_only_fields = ("id", "created_at", "tickets")

    def validate_seats(self, seats):
        for s in seats:
            if "row" not in s or "seat" not in s:
                raise serializers.ValidationError("Each seat must contain 'row' and 'seat'.")
        return seats

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        flight = validated_data["flight_id"]
        seats = validated_data["seats"]

        try:
            order = create_order_with_tickets(user=user, flight=flight, seats=seats)
        except SeatBookingError as e:
            raise serializers.ValidationError({"seats": str(e)}) from e

        return order
