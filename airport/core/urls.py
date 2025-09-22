from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    AirportViewSet, AirplaneTypeViewSet, AirplaneViewSet,
    RouteViewSet, CrewViewSet, FlightViewSet, OrderViewSet
)

router = DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("routes", RouteViewSet, basename="route")
router.register("crew", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [path("", include(router.urls))]
