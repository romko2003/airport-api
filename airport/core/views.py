from datetime import datetime
from django.db.models import F, Count
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Airport, AirplaneType, Airplane, Route, Crew, Flight, Order
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AirportSerializer, AirplaneTypeSerializer, AirplaneSerializer, AirplaneListSerializer,
    RouteSerializer, CrewSerializer,
    FlightSerializer, FlightListSerializer,
    OrderCreateSerializer, OrderListSerializer,
)

class BaseAdminCRUD(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)


class AirportViewSet(BaseAdminCRUD):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneTypeViewSet(BaseAdminCRUD):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(BaseAdminCRUD):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        return AirplaneListSerializer if self.action == "list" else AirplaneSerializer


class RouteViewSet(BaseAdminCRUD):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer


class CrewViewSet(BaseAdminCRUD):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(name="date", type=OpenApiTypes.DATE, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="source", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="destination", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
        OpenApiParameter(name="airplane", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
    ]
)
class FlightViewSet(BaseAdminCRUD):
    serializer_class = FlightSerializer
    queryset = Flight.objects.select_related("route__source", "route__destination", "airplane")\
        .prefetch_related("crew")\
        .annotate(
            available_tickets=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )

    def get_queryset(self):
        qs = super().get_queryset()
        date_str = self.request.query_params.get("date")
        src = self.request.query_params.get("source")
        dst = self.request.query_params.get("destination")
        airplane = self.request.query_params.get("airplane")

        if date_str:
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
                qs = qs.filter(departure_time__date=d)
            except ValueError:
                pass
        if src:
            qs = qs.filter(route__source_id=src)
        if dst:
            qs = qs.filter(route__destination_id=dst)
        if airplane:
            qs = qs.filter(airplane_id=airplane)
        return qs

    def get_serializer_class(self):
        return FlightListSerializer if self.action == "list" else FlightSerializer

    @action(detail=True, methods=["GET"], url_path="seat-map")
    def seat_map(self, request, pk=None):
        flight = self.get_object()
        taken = set(flight.tickets.values_list("row", "seat"))
        rows, seats = flight.airplane.rows, flight.airplane.seats_in_row
        schema = [
            {"row": r, "seats": [{"num": s, "taken": (r, s) in taken} for s in range(1, seats + 1)]}
            for r in range(1, rows + 1)
        ]
        return Response({"flight": flight.id, "rows": rows, "seats_in_row": seats, "map": schema})


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderCreateSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("tickets__flight")

    def get_serializer_class(self):
        return OrderListSerializer if self.action == "list" else OrderCreateSerializer

    def perform_create(self, serializer):
        serializer.save()
