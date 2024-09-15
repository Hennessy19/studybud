from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q  # this is provided by django to help with and | or searches bassing on multiple params
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required   # this is a decorator that will check if the user is logged in before they can access the view
from django.contrib.auth.forms import UserCreationForm # this is a form that is provided by django to help with user registration

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:  # this will check if the user is already logged in
            return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username').lower()  # this will convert the username to lowercase
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")  

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # adds the session to the db and the browser then logs the user in
            return redirect('home')
        else:
            messages.error(request, "Username OR password is incorrect")

    context = {'page':page}
    return render(request, 'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # this will save the form data to the user object but not to the db
            user.username = user.username.lower()  # this will convert the username to lowercase
            user.save()
            login(request, user)  # adds the session to the db and the browser then logs the user in
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")

    context = {'form':form, 'page':page}
    return render(request, 'base/login_register.html', context)




def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
                                ) # topic__name is used to filter the rooms based on the topic name,
                                  # __icontains is used to filter the rooms based on the topic name and is case insensitive
                                #   the Q is used to combine the filters to search for the rooms based on the topic name, name and description

    topics = Topic.objects.all()[0:5] #only get the first 5 items in the queryset
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)) # this will filter the messages based on the room topic name

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html',context)


def room(request,pk):
    print("Request",request)
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    # .order_by('-created') # this will order rooms by the created date and time and pass them to the template    
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') # this will get the message from the form from the field with the name body

        )
        room.participants.add(request.user) # this will add the user to the participants list
        return redirect("room", pk=room.id)

    context = {"room":room, "room_messages":room_messages, "participants":participants}
    return render(request, 'base/room.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics =Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) #this will retun back the specified value, but if it doesnt exist, will create it 

        Room.objects.create(
            host = request.user,
            topic=topic,
            name = request.POST.get('name'), #value being gotten from the form
            description = request.POST.get('description')

        )

        # form = RoomForm(request.POST) # this will get the data from the form
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        #     return redirect('home')
        
    context = {"form":form, "topics":topics} # this will pass the form to the template
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') # this will check if the user is logged in before they can access the view
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # this will prefill the form with the data from the room
    topics =Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here!!!!")
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) #this will retun back the specified value, but if it doesnt exist, will create it 
        form = RoomForm(request.POST, instance=room) # this will get the data from the form
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context = {"form":form, "topics":topics, "room":room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request,pk): #this deletes a room
    room =Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here!!!!")
    
    if request.method == "POST":
        room.delete()
        return redirect('home') 
    return render(request, 'base/delete.html',{'obj':room}) # this will pass the form to the template

@login_required(login_url='login')
def deleteMessage(request,pk): # this will delete a message
    message  =Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here!!!!")
    
    if request.method == "POST":
        message.delete()
        return redirect('home') 
    return render(request, 'base/delete.html',{'obj':message}) # this will pass the form to the template

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # this will get all the rooms that the user is a participant  
    room_messages =user.message_set.all()
    topics = Topic.objects.all() 
    context = {'user':user, 'rooms':rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html',context) # this will render the profile page

@login_required(login_url='login')
def updateUser(request):
    user = request.user 
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context = {"form":form}
    return render(request, 'base/update-user.html',context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    context = {"topics":topics}
    return render(request, 'base/topics.html',context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {"room_messages":room_messages}
    return render(request, 'base/activity.html', context)