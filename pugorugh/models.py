from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Dog(models.Model):
    name = models.CharField(max_length=100)
    image_filename = models.CharField(max_length=100)
    breed = models.CharField(blank=True, max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1)
    size = models.CharField(max_length=2)
    sterilized = models.BooleanField(default=False)


class UserDog(models.Model):
    user = models.ForeignKey(User)
    dog = models.ForeignKey(Dog)
    status = models.CharField(max_length=1)

    class Meta:
        unique_together = ['user', 'dog']


class UserPref(models.Model):
    user = models.OneToOneField(User, related_name='preferences')
    age = models.CharField(max_length=20, default='b,y,a,s')
    gender = models.CharField(max_length=20, default='m,f')
    size = models.CharField(max_length=20, default='s,m,l,xl')


def create_user_pref(sender, instance, created, **kwargs):
    """Create user preferences with defaults for new users."""
    if created:
        UserPref(user=instance).save()

post_save.connect(create_user_pref, sender=User)
