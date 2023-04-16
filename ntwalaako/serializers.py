from rest_framework import serializers
from .models import Driver, Ride, Rider

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['driver_id', 'wallet_balance']

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ['rider_id', 'driver_id', 'destination', 'cost', 'is_completed', 'preimage']


class CompleteRideSerializer(serializers.Serializer):
    payment_request = serializers.CharField(required=True)
    ride_id = serializers.CharField(required=True)

class SettleRideInvoiceSerializer(serializers.Serializer):
    ride_id = serializers.CharField(required=True)

class RiderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rider
        fields = ['rider_id', 'wallet_balance']
