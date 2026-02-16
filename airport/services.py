from __future__ import annotations

from typing import Iterable

from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from airport.models import Order, Ticket, Flight


class SeatBookingError(Exception):
    """Raised when booking seats fails due to validation or conflicts."""


@transaction.atomic
def create_order_with_tickets(*, user, flight: Flight, seats: Iterable[dict]) -> Order:
    """
    Creates an order and books seats (tickets) for a given flight.

    seats: iterable of {"row": int, "seat": int}

    Validations:
    - no duplicates in request
    - bounds: 1..rows and 1..seats_in_row
    - already taken seats are not allowed
    - atomic transaction
    """
    requested = []
    for s in seats:
        try:
            row = int(s["row"])
            seat = int(s["seat"])
        except (KeyError, TypeError, ValueError) as e:
            raise SeatBookingError("Each seat must contain integer 'row' and 'seat'.") from e
        requested.append((row, seat))

    if not requested:
        raise SeatBookingError("Seats list cannot be empty.")

    # duplicates in request
    requested_set = set(requested)
    if len(requested_set) != len(requested):
        raise SeatBookingError("Duplicate seats in request.")

    airplane = flight.airplane

    # bounds check
    for row, seat in requested_set:
        if not (1 <= row <= airplane.rows):
            raise SeatBookingError(f"Row {row} is out of range for airplane {airplane.name}.")
        if not (1 <= seat <= airplane.seats_in_row):
            raise SeatBookingError(f"Seat {seat} is out of range for airplane {airplane.name}.")

    # check already taken seats (single query + set intersection)
    rows = [r for r, _ in requested_set]
    existing = set(
        Ticket.objects.filter(flight=flight, row__in=rows).values_list("row", "seat")
    )
    taken = requested_set.intersection(existing)
    if taken:
        taken_sorted = sorted(taken)
        raise SeatBookingError(f"Some seats are already taken: {taken_sorted}")

    order = Order.objects.create(user=user)

    tickets = []
    for row, seat in requested_set:
        ticket = Ticket(
            flight=flight,
            order=order,
            row=row,
            seat=seat,
        )
        # Ticket.clean() checks bounds using flight.airplane (extra safety)
        try:
            ticket.full_clean()
        except DjangoValidationError as e:
            raise SeatBookingError(str(e.message_dict)) from e
        tickets.append(ticket)

    try:
        Ticket.objects.bulk_create(tickets)
    except IntegrityError as e:
        # DB unique constraint fallback (race condition safety)
        raise SeatBookingError("One or more seats are already taken.") from e

    return order
