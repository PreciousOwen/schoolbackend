from django.db import models
from django.conf import settings
from django.utils import timezone

class CorporateAccount(models.Model):
    name              = models.CharField(max_length=200, unique=True)
    billing_address   = models.TextField()
    contact_email     = models.EmailField()
    billing_cycle_day = models.PositiveSmallIntegerField(
        default=30,
        help_text="Day of month to generate invoices"
    )
    net_terms         = models.PositiveSmallIntegerField(
        default=30,
        help_text="Days until payment due after invoice date"
    )
    is_active         = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CorporateStaff(models.Model):
    """
    Links a User to a CorporateAccount, with optional end_date.
    Only active (no end_date or end_date >= today) links are honored.
    """
    user              = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='corporate_links'
    )
    corporate_account = models.ForeignKey(
        CorporateAccount,
        on_delete=models.CASCADE,
        related_name='staff'
    )
    start_date        = models.DateField(default=timezone.now)
    end_date          = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = [('user', 'corporate_account', 'start_date')]

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today and (self.end_date is None or self.end_date >= today)

    def __str__(self):
        return f"{self.user.username} → {self.corporate_account.name}"


class Invoice(models.Model):
    PENDING = 'pending'
    PAID    = 'paid'
    STATUS_CHOICES = [(PENDING, 'Pending'), (PAID, 'Paid')]

    corporate_account = models.ForeignKey(
        CorporateAccount,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    period_start      = models.DateField()
    period_end        = models.DateField()
    total_amount      = models.DecimalField(max_digits=10, decimal_places=2)
    status            = models.CharField(
                          max_length=10,
                          choices=STATUS_CHOICES,
                          default=PENDING
                       )
    pdf_file          = models.FileField(
                          upload_to='invoices/',
                          null=True, blank=True
                       )
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_start']
        unique_together = [('corporate_account', 'period_start', 'period_end')]

    def __str__(self):
        return f"Invoice {self.id} for {self.corporate_account.name} [{self.period_start}→{self.period_end}]"
