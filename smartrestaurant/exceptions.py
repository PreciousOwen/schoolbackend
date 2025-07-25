# smartrestaurant/exceptions.py

import logging
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    APIException, AuthenticationFailed, NotAuthenticated,
    PermissionDenied as DRFPermissionDenied, NotFound,
    ValidationError as DRFValidationError, Throttled
)

logger = logging.getLogger(__name__)


class SmartRestaurantAPIException(APIException):
    """Base exception for SmartRestaurant API"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'


class BusinessLogicError(SmartRestaurantAPIException):
    """Exception for business logic violations"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Business logic error occurred.'
    default_code = 'business_logic_error'


class ResourceNotAvailableError(SmartRestaurantAPIException):
    """Exception for resource availability issues"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource is not available.'
    default_code = 'resource_not_available'


class PaymentProcessingError(SmartRestaurantAPIException):
    """Exception for payment processing issues"""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed.'
    default_code = 'payment_error'


class ReservationConflictError(ResourceNotAvailableError):
    """Exception for reservation conflicts"""
    default_detail = 'Reservation conflict detected.'
    default_code = 'reservation_conflict'


class InsufficientStockError(ResourceNotAvailableError):
    """Exception for insufficient stock"""
    default_detail = 'Insufficient stock available.'
    default_code = 'insufficient_stock'


class OrderProcessingError(BusinessLogicError):
    """Exception for order processing issues"""
    default_detail = 'Order processing failed.'
    default_code = 'order_processing_error'


def custom_exception_handler(exc, context):
    """Custom exception handler for the API"""
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Get the view and request from context
    view = context.get('view')
    request = context.get('request')
    
    # Log the exception
    if response is not None:
        logger.warning(
            f"API Exception: {exc.__class__.__name__} - {str(exc)} "
            f"- View: {view.__class__.__name__ if view else 'Unknown'} "
            f"- User: {request.user if request and hasattr(request, 'user') else 'Anonymous'}"
        )
    else:
        logger.error(
            f"Unhandled Exception: {exc.__class__.__name__} - {str(exc)} "
            f"- View: {view.__class__.__name__ if view else 'Unknown'} "
            f"- User: {request.user if request and hasattr(request, 'user') else 'Anonymous'}",
            exc_info=True
        )
    
    # Handle specific exceptions
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data,
            'status_code': response.status_code,
            'timestamp': django_timezone.now().isoformat(),
        }
        
        # Add request ID if available
        if request and hasattr(request, 'META'):
            custom_response_data['request_id'] = request.META.get('HTTP_X_REQUEST_ID')
        
        # Customize response based on exception type
        if isinstance(exc, NotAuthenticated):
            custom_response_data['message'] = 'Authentication required'
            custom_response_data['code'] = 'authentication_required'
            
        elif isinstance(exc, (PermissionDenied, DRFPermissionDenied)):
            custom_response_data['message'] = 'Permission denied'
            custom_response_data['code'] = 'permission_denied'
            
        elif isinstance(exc, NotFound):
            custom_response_data['message'] = 'Resource not found'
            custom_response_data['code'] = 'not_found'
            
        elif isinstance(exc, (ValidationError, DRFValidationError)):
            custom_response_data['message'] = 'Validation error'
            custom_response_data['code'] = 'validation_error'
            
        elif isinstance(exc, Throttled):
            custom_response_data['message'] = 'Rate limit exceeded'
            custom_response_data['code'] = 'rate_limit_exceeded'
            custom_response_data['retry_after'] = exc.wait
            
        elif isinstance(exc, SmartRestaurantAPIException):
            custom_response_data['message'] = str(exc.detail)
            custom_response_data['code'] = exc.default_code
            
        else:
            custom_response_data['message'] = 'An unexpected error occurred'
            custom_response_data['code'] = 'internal_error'
        
        response.data = custom_response_data
        
    else:
        # Handle unhandled exceptions
        from django.utils import timezone
        
        custom_response_data = {
            'error': True,
            'message': 'Internal server error',
            'code': 'internal_error',
            'status_code': 500,
            'timestamp': timezone.now().isoformat(),
        }
        
        # Add request ID if available
        if request and hasattr(request, 'META'):
            custom_response_data['request_id'] = request.META.get('HTTP_X_REQUEST_ID')
        
        # Don't expose internal error details in production
        from django.conf import settings
        if settings.DEBUG:
            custom_response_data['debug_info'] = {
                'exception_type': exc.__class__.__name__,
                'exception_message': str(exc),
            }
        
        response = Response(
            custom_response_data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


class APIErrorCodes:
    """Centralized error codes for the API"""
    
    # Authentication & Authorization
    AUTHENTICATION_REQUIRED = 'authentication_required'
    INVALID_CREDENTIALS = 'invalid_credentials'
    PERMISSION_DENIED = 'permission_denied'
    TOKEN_EXPIRED = 'token_expired'
    
    # Validation
    VALIDATION_ERROR = 'validation_error'
    REQUIRED_FIELD_MISSING = 'required_field_missing'
    INVALID_FORMAT = 'invalid_format'
    INVALID_VALUE = 'invalid_value'
    
    # Business Logic
    BUSINESS_LOGIC_ERROR = 'business_logic_error'
    RESOURCE_NOT_AVAILABLE = 'resource_not_available'
    OPERATION_NOT_ALLOWED = 'operation_not_allowed'
    
    # Orders
    ORDER_NOT_FOUND = 'order_not_found'
    ORDER_ALREADY_PROCESSED = 'order_already_processed'
    INSUFFICIENT_STOCK = 'insufficient_stock'
    ORDER_CANNOT_BE_MODIFIED = 'order_cannot_be_modified'
    
    # Reservations
    RESERVATION_NOT_FOUND = 'reservation_not_found'
    RESERVATION_CONFLICT = 'reservation_conflict'
    TABLE_NOT_AVAILABLE = 'table_not_available'
    RESERVATION_CANNOT_BE_CANCELLED = 'reservation_cannot_be_cancelled'
    
    # Payments
    PAYMENT_FAILED = 'payment_failed'
    PAYMENT_ALREADY_PROCESSED = 'payment_already_processed'
    INVALID_PAYMENT_METHOD = 'invalid_payment_method'
    REFUND_NOT_ALLOWED = 'refund_not_allowed'
    
    # System
    INTERNAL_ERROR = 'internal_error'
    SERVICE_UNAVAILABLE = 'service_unavailable'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    MAINTENANCE_MODE = 'maintenance_mode'


def raise_business_error(message: str, code: str = None, status_code: int = None):
    """Helper function to raise business logic errors"""
    error = BusinessLogicError(detail=message)
    if code:
        error.default_code = code
    if status_code:
        error.status_code = status_code
    raise error


def raise_validation_error(message: str, field: str = None):
    """Helper function to raise validation errors"""
    if field:
        detail = {field: [message]}
    else:
        detail = {'non_field_errors': [message]}
    
    raise DRFValidationError(detail=detail)


def raise_not_found_error(resource: str = "Resource"):
    """Helper function to raise not found errors"""
    raise NotFound(detail=f"{resource} not found")


def raise_permission_error(message: str = "You do not have permission to perform this action"):
    """Helper function to raise permission errors"""
    raise DRFPermissionDenied(detail=message)
