from django.db import models
from django.db.models import Q, F


class Airport(models.Model):
    name = models.CharField(max_length=128, unique=True)
    closest_big_city = models.CharField(max_length=128)

    def __str__(self) -> str:
        return f"{self.name} ({self.closest_big_city})"


class AirplaneType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=64)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.PROTECT, related_name="airplanes")

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(rows__gt=0), name="airplane_rows_gt_0"),
            models.CheckConstraint(check=Q(seats_in_row__gt=0), name="airplane_seats_in_row_gt_0"),
        ]

    @property
    def capacity(self) -> int:
        return int(self.rows) * int(self.seats_in_row)

    def __str__(self) -> str:
        return f"{self.name} ({self.airplane_type})"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name="arrivals")
    distance = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("source", "destination"), name="route_unique_src_dst"),
            models.CheckConstraint(check=~Q(source=F("destination")), name="route_src_ne_dst"),
        ]

    def __str__(self):
        return f"{self.source} → {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.PROTECT, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights", blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(arrival_time__gt=F("departure_time")),
                name="flight_arrival_after_departure",
            )
        ]

    def __str__(self):
        return f"{self.route} @ {self.departure_time:%Y-%m-%d %H:%M}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("flight", "row", "seat"), name="unique_flight_row_seat"),
        ]

    def __str__(self):
        return f"{self.flight} — r{self.row}s{self.seat}"
