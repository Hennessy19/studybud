from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Q  # this is provided by django to help with and | or searches bassing on multiple params

# Create your views here.


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
                                ) # topic__name is used to filter the rooms based on the topic name,
                                  # __icontains is used to filter the rooms based on the topic name and is case insensitive
                                #   the Q is used to combine the filters to search for the rooms based on the topic name, name and description

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count}
    return render(request, 'base/home.html',context)
def room(request,pk):
    room = Room.objects.get(id=pk)
    context = {"room":room}
    return render(request, 'base/room.html',context)

def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST) # this will get the data from the form
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {"form":form} # this will pass the form to the template
    return render(request, 'base/room_form.html', context)

def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # this will prefill the form with the data from the room
    
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room) # this will get the data from the form
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {"form":form}
    return render(request, 'base/room_form.html', context)

def deleteRoom(request,pk):
    room =Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home') 
    return render(request, 'base/delete.html',{'obj':room}) # this will pass the form to the template