# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from locations.models import Location
from taggit.managers import TaggableManager

class Category(models.Model):
    """
    User Idea Categories basic model
    """
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=1024)
    
    def __unicode__(self):
        return self.name

class Idea(models.Model):
    """
    User Idea basic model
    """
    creator = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=2048, null=True, blank=True,)
    categories = models.ManyToManyField(Category, verbose_name=_('Categories'),
                                        null=True, blank=True,)
    location = models.ForeignKey(Location)
    status = models.BooleanField(default=True)
    # Track changes to mark item as edited when user changes it.
    # Fixme - after saving tags this field is True which is not desired effect.
    edited = models.BooleanField(default=False)
    tags = TaggableManager()
    
    def get_votes(self):
        votes_total = self.vote_set
        votes_up = len(votes_total.filter(vote=True))
        votes_down = len(votes_total.filter(vote=False))
        return votes_up - votes_down

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.edited = True
            self.date_edited = timezone.now()
        super(Idea, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('ideas:details', kwargs={'pk':self.pk})
    
    def __unicode__(self):
        return self.name
        
    
class Vote(models.Model):
    """
    Users can vote up or down on ideas
    """
    user = models.ForeignKey(User)
    idea = models.ForeignKey(Idea)
    vote = models.BooleanField(default=False)
    date_voted = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.vote
