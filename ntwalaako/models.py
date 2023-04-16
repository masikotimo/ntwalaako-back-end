from django.db import models

class Driver(models.Model):
    driver_id = models.IntegerField(primary_key=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2)

class Ride(models.Model):
    rider_id = models.IntegerField()
    driver_id = models.IntegerField()
    destination = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    preimage = models.BinaryField()

class Rider(models.Model):
    rider_id = models.IntegerField(primary_key=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2)
