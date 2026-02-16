from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to",
    )
    distance = models.PositiveIntegerField(help_text="Distance in km")

    class Meta:
        ordering = ["source__name", "destination__name"]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(source=models.F("destination")),
                name="route_source_not_equal_destination",
            ),
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_route_source_destination",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.source.name} -> {self.destination.name} ({self.distance} km)"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.PROTECT,
        related_name="airplanes",
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name} ({self.airplane_type.name})"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name="unique_crew_first_last",
            )
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name="flights",
    )
    crew = models.ManyToManyField(Crew, related_name="flights", blank=True)

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(arrival_time__gt=models.F("departure_time")),
                name="flight_arrival_after_departure",
            )
        ]

    def __str__(self) -> str:
        return f"Flight #{self.pk} {self.route} ({self.departure_time.isoformat()})"


class Order(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} by {self.user}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        ordering = ["flight_id", "row", "seat"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"],
                name="unique_ticket_per_flight_seat",
            ),
        ]

    def clean(self) -> None:
        airplane = self.flight.airplane
        if not (1 <= self.row <= airplane.rows):
            raise ValidationError({"row": "Row is out of range for this airplane."})
        if not (1 <= self.seat <= airplane.seats_in_row):
            raise ValidationError({"seat": "Seat is out of range for this airplane."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Ticket F{self.flight_id} R{self.row} S{self.seat}"
