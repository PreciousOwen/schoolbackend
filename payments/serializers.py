# payments/serializers.py

from rest_framework import serializers
from decimal import Decimal
from .models import PaymentMethod, Payment, Refund


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment methods"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'type', 'is_default', 'last_four', 'brand', 
            'exp_month', 'exp_year', 'created_at'
        ]
        read_only_fields = [
            'id', 'last_four', 'brand', 'exp_month', 'exp_year', 'created_at'
        ]


class CreatePaymentMethodSerializer(serializers.Serializer):
    """Serializer for creating payment methods via Stripe"""
    stripe_payment_method_id = serializers.CharField(max_length=255)
    is_default = serializers.BooleanField(default=False)


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions"""
    payment_method_details = PaymentMethodSerializer(source='payment_method', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'payment_method', 'payment_method_details',
            'amount', 'currency', 'status', 'processing_fee', 'net_amount',
            'failure_reason', 'receipt_url', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_payment_intent_id', 'stripe_charge_id',
            'processing_fee', 'net_amount', 'failure_reason', 
            'receipt_url', 'created_at', 'updated_at'
        ]


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating payment intents"""
    order_id = serializers.UUIDField()
    payment_method_id = serializers.UUIDField(required=False)
    save_payment_method = serializers.BooleanField(default=False)
    
    def validate_order_id(self, value):
        from orders.models import Order
        try:
            order = Order.objects.get(id=value)
            if order.status != Order.PENDING:
                raise serializers.ValidationError("Order must be pending to process payment")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming payments"""
    payment_intent_id = serializers.CharField(max_length=255)


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refunds"""
    
    class Meta:
        model = Refund
        fields = [
            'id', 'payment', 'amount', 'reason', 'status', 
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_refund_id', 'status', 'created_at', 'updated_at'
        ]
    
    def validate_amount(self, value):
        payment = self.context.get('payment')
        if payment:
            total_refunded = sum(
                refund.amount for refund in payment.refunds.filter(
                    status__in=[Refund.SUCCEEDED, Refund.PENDING]
                )
            )
            if total_refunded + value > payment.amount:
                raise serializers.ValidationError(
                    "Refund amount exceeds available balance"
                )
        return value


class CreateRefundSerializer(serializers.Serializer):
    """Serializer for creating refunds"""
    payment_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(max_length=255, required=False)
    
    def validate_payment_id(self, value):
        try:
            payment = Payment.objects.get(id=value)
            if payment.status != Payment.SUCCEEDED:
                raise serializers.ValidationError("Can only refund successful payments")
            return value
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Payment not found")
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be positive")
        return value
