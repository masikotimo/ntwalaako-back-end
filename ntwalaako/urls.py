from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, RideViewSet, RiderViewSet,RideRequestView,RideCompletionView

router = DefaultRouter()
router.register(r'drivers', DriverViewSet)
router.register(r'rides', RideViewSet)
router.register(r'riders', RiderViewSet)

urlpatterns = router.urls
