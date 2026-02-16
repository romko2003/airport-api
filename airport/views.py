from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order
from airport.permissions import IsAdminOrReadOnly
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name", "closest_big_city")
    ordering_fields = ("name",)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ("source", "destination")
    search_fields = ("source__name", "destination__name")
    ordering_fields = ("distance", "source__name", "destination__name")


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name",)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ("airplane_type",)
    search_fields = ("name", "airplane_type__name")
    ordering_fields = ("name", "rows", "seats_in_row")


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("first_name", "last_name")
    ordering_fields = ("last_name", "first_name")


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.select_related(
            "route__source",
            "route__destination",
            "airplane__airplane_type",
        )
        .prefetch_related("crew")
    )
    permission_classes = (IsAdminOrReadOnly,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = (
        "route__source",
        "route__destination",
        "airplane",
        "airplane__airplane_type",
    )
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "airplane__name",
    )
    ordering_fields = ("departure_time", "arrival_time")

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightDetailSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    For now:
    - users can list their own orders
    - create empty order (tickets logic will be implemented in PR #4)
    """
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("tickets__flight")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
