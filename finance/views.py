from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import has_role, IsAdmin
from .models import Product, Payment
from .serializers import ProductSerializer, PaymentSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [IsAuthenticated(), has_role('staff', 'admin')()]
        return [IsAuthenticated(), IsAdmin()]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, has_role('staff', 'admin')]

    def perform_create(self, serializer):
        user = self.request.user
        profile = getattr(user, 'staff', None) or getattr(user, 'admin', None)
        handled_by = profile.name if profile else user.username
        try:
            serializer.save(handled_by=handled_by)
        except IntegrityError:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                'This student has already paid for this session'
            )
