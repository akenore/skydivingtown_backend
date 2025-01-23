from django.db.models.signals import pre_save
from django.dispatch import receiver
import shortuuid
from contract.models import Company


def generate_ref_code():
    return shortuuid.ShortUUID().random(length=10)


@receiver(pre_save, sender=Company)
def add_ref_code(sender, instance, **kwargs):
    if not instance.ref:
        instance.ref = generate_ref_code()
        while Company.objects.filter(ref=instance.ref).exists():
            instance.ref = generate_ref_code()
