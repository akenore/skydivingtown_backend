from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from autoslug import AutoSlugField
from django_countries.fields import CountryField
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from birthday import BirthdayField, BirthdayManager

class EventOption(models.Model):
    name = models.CharField(_("Option name"), max_length=100)
    amount = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    slug = AutoSlugField(populate_from='name', unique=True)
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Event Option")
        verbose_name_plural = _("Event Options")

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(_("Event name"), max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    published = models.DateTimeField(auto_now_add=True)
    options = models.ManyToManyField(EventOption, verbose_name=_("Event Options"), blank=True)
    amount = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    description = models.TextField(_("Description"), blank=True, null=True)

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.name


class EventDate(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_dates')
    date = models.DateField(_("Event date"))

    class Meta:
        verbose_name = _("Event Date")
        verbose_name_plural = _("Event Dates")

    def __str__(self):
        return self.date.strftime("%d %B %Y")


class EventTime(models.Model):
    event_date = models.ForeignKey(EventDate, on_delete=models.CASCADE, related_name='event_times')
    time = models.TimeField(_("Event time"))
    maxSubscribers = models.PositiveIntegerField(_("Max number of subscribers"), default=6)

    class Meta:
        verbose_name = _("Event Time")
        verbose_name_plural = _("Event Times")
        ordering = ['time']
        constraints = [
            models.UniqueConstraint(fields=['event_date', 'time'], name='unique_event_time')
        ]

    def clean(self):
        if self.pk and self.maxSubscribers < self.current_subscriber_count:
            raise ValidationError({
                'maxSubscribers': _('Max subscribers cannot be less than current subscriber count (%(count)d)')
                % {'count': self.current_subscriber_count}
            })

    @property
    def current_subscriber_count(self):
        return self.subscribers.count() if hasattr(self, 'subscribers') else 0

    def get_available_slots(self):
        return max(0, self.maxSubscribers - self.current_subscriber_count)

    def is_full(self):
        return self.current_subscriber_count >= self.maxSubscribers

    def __str__(self):
        return f"{self.time.strftime('%H:%M')} ({self.get_available_slots()} places available)"


class Subscriber(models.Model):
    published = models.DateTimeField(auto_now_add=True)

    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
    ]

    ALTITUDE_CHOICES = [
        ('3000', _('3 000 m (10 000 feet)')),
        ('3200', _('3 200 m (10 500 feet)')),
        ('3500', _('3 500 m (11 500 feet)')),
    ]

    SKYDIVER_OPTIONS = [
        ('tandem', 'Tandem (Beginner)'),
        ('solo', 'Solo'),
        ('experienced', 'Experienced'),
    ]

    eventDate = models.ForeignKey(
        EventDate, on_delete=models.PROTECT, related_name='subscribers', verbose_name=_("Event Date")
    )
    eventTime = models.ForeignKey(
        EventTime, on_delete=models.PROTECT, related_name='subscribers', verbose_name=_("Event Time")
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Enter a valid phone number (e.g., +123456789). Max 15 digits.")
    )

    email = models.EmailField(_("Email"))
    name = models.CharField(_("First Name"), max_length=100)
    surname = models.CharField(_("Last name"), max_length=100)
    phone = models.CharField(_("Phone"), validators=[phone_regex], max_length=17, blank=True)
    birthDate = BirthdayField(_("Birth Date"))
    country = CountryField(blank_label=_("(Select country)"))
    region = models.CharField(_("City"), max_length=100)
    gender = models.CharField(_("Gender"), max_length=1, choices=GENDER_CHOICES, default='M')
    altitude = models.CharField(
        _("At what altitude would you like to jump from a plane?"), max_length=5, choices=ALTITUDE_CHOICES, default='3400'
    )
    skydiverOption = models.CharField(
        _("Are you a skydiver?"), max_length=12, choices=SKYDIVER_OPTIONS, default='tandem'
    )
    options = models.ManyToManyField(EventOption, verbose_name=_("Selected Options"), blank=True)

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")

    def __str__(self):
        return f"{self.eventDate}: {self.name} {self.surname} - {self.email}"


class Payment(models.Model):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(_("Total Amount"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return f"Payment for {self.subscriber.name} {self.subscriber.surname} - {self.amount}"

    def calculate_total_amount(self):
        event_price = self.subscriber.eventDate.event.amount
        options_total = sum(option.amount for option in self.subscriber.options.all()) if self.subscriber.options.exists() else 0
        return event_price + options_total

    def save(self, *args, **kwargs):
        self.amount = self.calculate_total_amount()
        super().save(*args, **kwargs)
