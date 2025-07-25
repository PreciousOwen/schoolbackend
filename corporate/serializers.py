# corporate/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CorporateAccount, CorporateStaff, Invoice

User = get_user_model()


class CorporateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateAccount
        fields = '__all__'
        read_only_fields = ['is_active']


class CorporateStaffSerializer(serializers.ModelSerializer):
    # show the username in GETs
    user = serializers.StringRelatedField(read_only=True)
    # accept a user PK in POSTs/PATCHes
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    # same pattern for the account
    corporate_account = serializers.StringRelatedField(read_only=True)
    corporate_account_id = serializers.PrimaryKeyRelatedField(
        queryset=CorporateAccount.objects.all(),
        source='corporate_account',
        write_only=True
    )

    class Meta:
        model = CorporateStaff
        fields = [
            'id',
            'user', 'user_id',
            'corporate_account', 'corporate_account_id',
            'start_date', 'end_date',
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    corporate_account = serializers.StringRelatedField(read_only=True)
    corporate_account_id = serializers.PrimaryKeyRelatedField(
        queryset=CorporateAccount.objects.all(),
        source='corporate_account',
        write_only=True
    )

    class Meta:
        model = Invoice
        fields = [
            'id',
            'corporate_account', 'corporate_account_id',
            'period_start', 'period_end',
            'total_amount', 'status', 'pdf_file', 'created_at'
        ]
        read_only_fields = ['total_amount', 'status', 'created_at']
