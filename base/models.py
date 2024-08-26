from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) #when a user gets deleted, delete the room as well
    topic = models.ForeignKey('Topic', on_delete=models.SET_NULL, null=True) #when a topic gets deleted, set the room's topic to null, also we put the string 'Topic' in quotes because the Topic class is defined after the Room class
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #null=True means that this field can exist as empty in the db, blank= True means it can be empty on saving
    participants = models.ManyToManyField(User, related_name='participants', blank=True) #many to many relationship with the User model, related_name is used to access the participants of a room
    updated = models.DateTimeField(auto_now=True) #auto_now takes a timestamp everytime the record is updated
    created = models.DateTimeField(auto_now_add=True) #auto_now_add takes a timestamp only for the first time the record is created

    class Meta:
        ordering = ['-updated', '-created'] #ordering the rooms by updated and created fields in descending order, the '-' sign means descending order

    #return string representation of the class  in the admin panel
    def __str__(self):  
        return self.name
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #when a user gets deleted, delete the messages as well
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #when a room gets deleted, delete the messages in the room as well
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]  

class Topic(models.Model):
    name = models.CharField(max_length=200)
    # description = models.TextField(null=True, blank=True)
    # updated = models.DateTimeField(auto_now=True)
    # created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name