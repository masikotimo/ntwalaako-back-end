from rest_framework import viewsets,generics
from .models import Driver, Ride, Rider
from .serializers import CompleteRideSerializer, DriverSerializer, RideSerializer, RiderSerializer, SettleRideInvoiceSerializer
from lnd_grpc import Client
from constants import lnd_dir, tls_cert_path, grpc_port, grpc_host, macaroon_path, network, tls_cert_path1, macaroon_path1, grpc_port1
import hashlib
import secrets
import time
from rest_framework.response import Response


lnd = Client(lnd_dir = lnd_dir,macaroon_path= macaroon_path, tls_cert_path= tls_cert_path,network = network,grpc_host= grpc_host,grpc_port=grpc_port)

lnd1 = Client(lnd_dir = lnd_dir,macaroon_path= macaroon_path1, tls_cert_path= tls_cert_path1,network = network,grpc_host= grpc_host,grpc_port=grpc_port1)




class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

class RiderViewSet(viewsets.ModelViewSet):
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer



class RideRequestView(generics.CreateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer


    def get(self, request, *args, **kwargs):
        ride_id = kwargs.get('pk') # assuming you are using primary key as URL parameter
        try:
            ride = Ride.objects.get(pk=ride_id)
            serializer = self.serializer_class(ride)
            return Response(serializer.data)
        except Ride.DoesNotExist:
            return Response({'message': 'Ride not found.'}, status=404)

    def create(self, request, *args, **kwargs):
        rider_id = request.data['rider_id']
        driver_id = request.data['driver_id']
        destination = request.data['destination']
        cost = int(request.data['cost']) 

        rider = Rider.objects.get(rider_id=rider_id)
        driver = Driver.objects.get(driver_id=driver_id)

        if rider.wallet_balance >= cost:

            preimage = secrets.token_bytes(32)

            print('my preimage',preimage)
            myhash = hashlib.sha256(preimage).digest()
            
            invoice = lnd.add_hold_invoice(value=int(cost), memo="pay_for_ride", hash=myhash)
            payment_request = invoice.payment_request
            ride = Ride() 
            ride.rider_id = rider_id
            ride.driver_id = driver_id
            ride.destination = destination
            ride.preimage = preimage
            ride.cost = cost
            ride.save()
            rider.wallet_balance -= cost
            rider.save()
            return Response({'payment_request': payment_request,})
        else:
            return Response({'message': 'Insufficient balance in rider\'s wallet.'})



class RideCompletionView(generics.UpdateAPIView):
    queryset = Ride.objects.all()
    serializer_class = CompleteRideSerializer

    def update(self, request, *args, **kwargs):
        ride_id = request.data['ride_id']
        payment_request = request.data['payment_request']

        try:
            ride = Ride.objects.get(pk=ride_id)
            if not ride.is_completed:
                # Verify preimage
                # myhash = hashlib.sha256(preimage).digest()
                # if ride.preimage == myhash:
                #     # Mark ride as completed
                #     ride.is_completed = True
                #     ride.save()

                #     # Transfer payment to driver
                #     driver = ride.driver
                #     driver.wallet_balance += ride.cost
                #     driver.save()

                response = lnd1.send_payment(payment_request=payment_request)
                print("rider pays:", response)

                return Response({'message': 'Ride completed successfully'})
                # else:
                #     return Response({'message': 'Invalid preimage'})
            else:
                return Response({'message': 'Ride already completed'})
        except Ride.DoesNotExist:
            return Response({'message': 'Ride not found'})



class SettleRideInvoiceView(generics.UpdateAPIView):
    queryset = Ride.objects.all()
    serializer_class = SettleRideInvoiceSerializer

    def update(self, request, *args, **kwargs):
        ride_id = request.data['ride_id']

        try:
            ride = Ride.objects.get(pk=ride_id)
            if not ride.is_completed:
                # Verify preimage
                # myhash = hashlib.sha256(preimage).digest()
                if ride.preimage is not  None:
                    # Mark ride as completed
                    ride.is_completed = True
                    ride.save()
                    print("gotten preimage",ride.preimage)
                    resp = lnd.settle_invoice(preimage=ride.preimage)
                    print("Settle Invoice Response:", resp)

                    # Transfer payment to driver
                    driver = ride.driver
                    driver.wallet_balance += ride.cost
                    driver.save()

                    return Response({'message': 'Ride payment fuly settled'})
                else:
                    return Response({'message': 'Invalid preimage'})
            else:
                return Response({'message': 'Ride already completed'})
        except Ride.DoesNotExist:
            return Response({'message': 'Ride not found'})