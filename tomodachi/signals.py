from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from . models import *

@receiver(pre_delete, sender=AppUser)
def pre_delete_factory(sender, instance, **kwargs):
    # False so FileField doesn't save the model.
    instance.profile_image.delete(save=False)

@receiver(pre_delete, sender=Post)
def pre_delete_factory(sender, instance, **kwargs):
    # False so FileField doesn't save the model.
    instance.image.delete(save=False)