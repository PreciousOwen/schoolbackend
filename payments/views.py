# payments/views.py

import stripe
import logging
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from orders.models import Order
from .models import PaymentMethod, Payment, Refund
from .serializers import (
    PaymentMethodSerializer, CreatePaymentMethodSerializer,
    PaymentSerializer, CreatePaymentIntentSerializer,
    ConfirmPaymentSerializer, RefundSerializer, CreateRefundSerializer
)
from .services import StripeService

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """Manage customer payment methods"""
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePaymentMethodSerializer
        return PaymentMethodSerializer

    @method_decorator(ratelimit(key='user', rate='10/min', method='POST'))
    def create(self, request, *args, **kwargs):
        """Create a new payment method"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            stripe_pm_id = serializer.validated_data['stripe_payment_method_id']
            is_default = serializer.validated_data.get('is_default', False)

            # Get payment method details from Stripe
            stripe_pm = stripe.PaymentMethod.retrieve(stripe_pm_id)

            # Create payment method
            payment_method = StripeService.create_payment_method(
                user=request.user,
                stripe_payment_method=stripe_pm,
                is_default=is_default
            )

            response_serializer = PaymentMethodSerializer(payment_method)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment method: {e}")
            return Response(
                {'error': 'Failed to create payment method'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating payment method: {e}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set a payment method as default"""
        payment_method = self.get_object()

        # Remove default from other payment methods
        PaymentMethod.objects.filter(
            customer=request.user, is_default=True
        ).update(is_default=False)

        # Set this one as default
        payment_method.is_default = True
        payment_method.save()

        serializer = self.get_serializer(payment_method)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """View payment transactions"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__customer=self.request.user)


class PaymentIntentView(APIView):
    """Create and confirm payment intents"""
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='20/min', method='POST'))
    def post(self, request):
        """Create a payment intent"""
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order_id = serializer.validated_data['order_id']
            payment_method_id = serializer.validated_data.get('payment_method_id')
            save_payment_method = serializer.validated_data.get('save_payment_method', False)

            order = Order.objects.get(id=order_id, customer=request.user)

            # Create payment intent
            payment_intent = StripeService.create_payment_intent(
                order=order,
                payment_method_id=payment_method_id,
                save_payment_method=save_payment_method
            )

            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            })

        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return Response(
                {'error': 'Failed to create payment intent'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConfirmPaymentView(APIView):
    """Confirm a payment intent"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Confirm payment intent"""
        serializer = ConfirmPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment_intent_id = serializer.validated_data['payment_intent_id']
            payment = StripeService.confirm_payment(payment_intent_id)

            response_serializer = PaymentSerializer(payment)
            return Response(response_serializer.data)

        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            return Response(
                {'error': 'Failed to confirm payment'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefundViewSet(viewsets.ModelViewSet):
    """Manage refunds"""
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(payment__order__customer=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateRefundSerializer
        return RefundSerializer

    def create(self, request, *args, **kwargs):
        """Create a refund"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can create refunds'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment_id = serializer.validated_data['payment_id']
            amount = serializer.validated_data['amount']
            reason = serializer.validated_data.get('reason', '')

            payment = Payment.objects.get(id=payment_id)
            refund = StripeService.create_refund(payment, amount, reason)

            response_serializer = RefundSerializer(refund)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error creating refund: {e}")
            return Response(
                {'error': 'Failed to create refund'},
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeWebhookView(APIView):
    """Handle Stripe webhooks"""
    permission_classes = []  # No authentication required for webhooks

    def post(self, request):
        """Handle Stripe webhook events"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            logger.error("Invalid payload in Stripe webhook")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in Stripe webhook")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            StripeService.handle_webhook(event['type'], event['data'])
            return Response({'status': 'success'})
        except Exception as e:
            logger.error(f"Error handling Stripe webhook: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
