from django.db import models
from django.urls import reverse
from autoslug import AutoSlugField
from django.utils.translation import gettext as _


class Company(models.Model):
    name = models.CharField(_("Company Name"), max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True)
    published = models.DateTimeField(auto_now=False, auto_now_add=True)
    email = models.EmailField(_("Email"), max_length=254)
    countryCode = models.CharField(_("Country code"), max_length=5, default='+216', help_text=_("Add your country code like +216 or 00216"))
    phone = models.CharField(_("Phone"), max_length=50)
    ref = models.CharField(_("Generated code"), max_length=11, unique=True)
    discount = models.IntegerField(_("Discount %"), default="0")
    valid = models.BooleanField(_("Validated company"), default=False)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("company", kwargs={"slug": self.slug})
