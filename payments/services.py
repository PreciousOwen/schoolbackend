# payments/services.py

import stripe
import logging
from django.conf import settings
from django.db import transaction
from decimal import Decimal
from typing import Optional

from orders.models import Order
from .models import PaymentMethod, Payment, Refund

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for Stripe payment processing"""
    
    @staticmethod
    def create_payment_method(user, stripe_payment_method, is_default=False):
        """Create a payment method from Stripe PM"""
        with transaction.atomic():
            # If setting as default, remove default from others
            if is_default:
                PaymentMethod.objects.filter(
                    customer=user, is_default=True
                ).update(is_default=False)
            
            # Extract card details if it's a card
            card_data = {}
            if stripe_payment_method.type == 'card':
                card = stripe_payment_method.card
                card_data = {
                    'last_four': card.last4,
                    'brand': card.brand,
                    'exp_month': card.exp_month,
                    'exp_year': card.exp_year,
                }
            
            payment_method = PaymentMethod.objects.create(
                customer=user,
                stripe_payment_method_id=stripe_payment_method.id,
                type=stripe_payment_method.type,
                is_default=is_default,
                **card_data
            )
            
            return payment_method
    
    @staticmethod
    def create_payment_intent(order: Order, payment_method_id: Optional[str] = None, 
                            save_payment_method: bool = False):
        """Create a Stripe payment intent for an order"""
        
        # Calculate amount in cents
        amount_cents = int(order.total * 100)
        
        # Base payment intent data
        intent_data = {
            'amount': amount_cents,
            'currency': settings.DEFAULT_CURRENCY.lower(),
            'metadata': {
                'order_id': str(order.id),
                'customer_id': str(order.customer.id),
            },
            'automatic_payment_methods': {'enabled': True},
        }
        
        # Add payment method if provided
        if payment_method_id:
            try:
                payment_method = PaymentMethod.objects.get(
                    id=payment_method_id, 
                    customer=order.customer
                )
                intent_data['payment_method'] = payment_method.stripe_payment_method_id
                intent_data['confirmation_method'] = 'manual'
                intent_data['confirm'] = True
            except PaymentMethod.DoesNotExist:
                raise ValueError("Payment method not found")
        
        # Setup future usage if saving payment method
        if save_payment_method:
            intent_data['setup_future_usage'] = 'off_session'
        
        # Create the payment intent
        payment_intent = stripe.PaymentIntent.create(**intent_data)
        
        # Create local payment record
        Payment.objects.create(
            order=order,
            payment_method_id=payment_method_id if payment_method_id else None,
            stripe_payment_intent_id=payment_intent.id,
            amount=order.total,
            currency=settings.DEFAULT_CURRENCY,
            status=Payment.PENDING
        )
        
        return payment_intent
    
    @staticmethod
    def confirm_payment(payment_intent_id: str):
        """Confirm a payment intent and update local records"""
        try:
            # Retrieve the payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Update local payment record
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            
            if payment_intent.status == 'succeeded':
                payment.status = Payment.SUCCEEDED
                payment.stripe_charge_id = payment_intent.latest_charge
                payment.receipt_url = payment_intent.charges.data[0].receipt_url if payment_intent.charges.data else ''
                
                # Update order status
                payment.order.status = Order.PAID
                payment.order.save()
                
            elif payment_intent.status == 'requires_action':
                payment.status = Payment.PROCESSING
            elif payment_intent.status in ['canceled', 'payment_failed']:
                payment.status = Payment.FAILED
                payment.failure_reason = payment_intent.last_payment_error.message if payment_intent.last_payment_error else 'Payment failed'
            
            payment.save()
            return payment
            
        except Payment.DoesNotExist:
            logger.error(f"Payment not found for intent {payment_intent_id}")
            raise
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {e}")
            raise
    
    @staticmethod
    def create_refund(payment: Payment, amount: Decimal, reason: str = ''):
        """Create a refund for a payment"""
        try:
            # Create refund in Stripe
            stripe_refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_intent_id,
                amount=int(amount * 100),  # Convert to cents
                reason='requested_by_customer' if not reason else 'duplicate',
                metadata={
                    'payment_id': str(payment.id),
                    'order_id': str(payment.order.id),
                    'reason': reason
                }
            )
            
            # Create local refund record
            refund = Refund.objects.create(
                payment=payment,
                stripe_refund_id=stripe_refund.id,
                amount=amount,
                reason=reason,
                status=Refund.PENDING if stripe_refund.status == 'pending' else Refund.SUCCEEDED
            )
            
            # Update payment status if fully refunded
            total_refunded = sum(
                r.amount for r in payment.refunds.filter(status=Refund.SUCCEEDED)
            )
            if total_refunded >= payment.amount:
                payment.status = Payment.REFUNDED
            elif total_refunded > 0:
                payment.status = Payment.PARTIALLY_REFUNDED
            payment.save()
            
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating refund: {e}")
            raise
    
    @staticmethod
    def handle_webhook(event_type: str, event_data: dict):
        """Handle Stripe webhook events"""
        try:
            if event_type == 'payment_intent.succeeded':
                payment_intent = event_data['object']
                StripeService.confirm_payment(payment_intent['id'])
                
            elif event_type == 'payment_intent.payment_failed':
                payment_intent = event_data['object']
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent['id']
                )
                payment.status = Payment.FAILED
                payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
                payment.save()
                
            elif event_type == 'charge.dispute.created':
                # Handle chargebacks
                charge = event_data['object']
                try:
                    payment = Payment.objects.get(stripe_charge_id=charge['id'])
                    # You might want to create a Dispute model to track these
                    logger.warning(f"Chargeback created for payment {payment.id}")
                except Payment.DoesNotExist:
                    logger.error(f"Payment not found for charge {charge['id']}")
                    
        except Exception as e:
            logger.error(f"Error handling webhook {event_type}: {e}")
            raise


class PaymentCalculator:
    """Helper class for payment calculations"""
    
    @staticmethod
    def calculate_processing_fee(amount: Decimal, payment_method_type: str = 'card') -> Decimal:
        """Calculate processing fees based on payment method"""
        # Stripe fees: 2.9% + 30¢ for cards
        if payment_method_type == 'card':
            return (amount * Decimal('0.029')) + Decimal('0.30')
        return Decimal('0.00')
    
    @staticmethod
    def calculate_tax(subtotal: Decimal, tax_rate: Decimal = Decimal('0.08')) -> Decimal:
        """Calculate tax amount"""
        return subtotal * tax_rate
    
    @staticmethod
    def calculate_tip(subtotal: Decimal, tip_percentage: Decimal) -> Decimal:
        """Calculate tip amount"""
        return subtotal * (tip_percentage / 100)
