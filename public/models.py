from django.db import models
from django.urls import reverse
from autoslug import AutoSlugField
from django.utils.translation import gettext as _
from tinymce.models import HTMLField


class Page(models.Model):
     name = models.CharField(_("Page Name"), max_length=100)
     slug = AutoSlugField(populate_from='name', unique=True)
     published = models.DateTimeField(auto_now=False, auto_now_add=True)
     content = HTMLField()
     

     class Meta:
          verbose_name = _("Page")
          verbose_name_plural = _("Pages")

     def __str__(self):
          return self.name

     def get_absolute_url(self):
          return reverse("Page_detail", kwargs={"pk": self.pk})
