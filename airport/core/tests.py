from datetime import datetime, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from core.models import Airport, AirplaneType, Airplane, Route, Flight, Order, Ticket

User = get_user_model()

FLIGHTS_URL = reverse("flight-list")
ORDERS_URL = reverse("orders-list")

def seat_map_url(pk: int) -> str:
    return reverse("flight-seat-map", args=[pk])


class BaseSetupMixin:
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser("admin@example.com", "adminpass")
        self.user = User.objects.create_user("user@example.com", "userpass")

        self.src = Airport.objects.create(name="Kyiv ZH", closest_big_city="Kyiv")
        self.dst = Airport.objects.create(name="Paris CDG", closest_big_city="Paris")
        self.tp = AirplaneType.objects.create(name="A320")
        self.plane = Airplane.objects.create(name="UR-AAA", rows=2, seats_in_row=3, airplane_type=self.tp)
        self.route = Route.objects.create(source=self.src, destination=self.dst, distance=2400)

        now = datetime.utcnow()
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.plane,
            departure_time=now + timedelta(days=1),
            arrival_time=now + timedelta(days=1, hours=3),
        )


class FlightsApiTests(BaseSetupMixin, APITestCase):
    def test_list_flights_filters_and_available(self):
        res = self.client.get(FLIGHTS_URL, {"source": self.src.id, "destination": self.dst.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        item = res.data["results"][0]
        self.assertIn("available_tickets", item)
        self.assertEqual(item["available_tickets"], 6)  # 2*3

    def test_seat_map_marks_taken(self):
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(order=order, flight=self.flight, row=1, seat=1)
        res = self.client.get(seat_map_url(self.flight.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        row1 = next(r for r in res.data["map"] if r["row"] == 1)
        seat1 = next(s for s in row1["seats"] if s["num"] == 1)
        self.assertTrue(seat1["taken"])


class OrdersApiTests(BaseSetupMixin, APITestCase):
    def test_create_order_happy_path(self):
        self.client.force_authenticate(self.user)
        payload = {"tickets": [
            {"flight": self.flight.id, "row": 1, "seat": 2},
            {"flight": self.flight.id, "row": 2, "seat": 3},
        ]}
        res = self.client.post(ORDERS_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Ticket.objects.filter(order__user=self.user).count(), 2)

    def test_create_order_rejects_taken_or_out_of_bounds(self):
        self.client.force_authenticate(self.user)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(order=order, flight=self.flight, row=1, seat=1)

        res1 = self.client.post(ORDERS_URL, {"tickets": [{"flight": self.flight.id, "row": 1, "seat": 1}]}, format="json")
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)

        res2 = self.client.post(ORDERS_URL, {"tickets": [{"flight": self.flight.id, "row": 99, "seat": 1}]}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
