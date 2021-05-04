
# Create your views here.
from django.shortcuts import render ,redirect
from django.contrib.auth import authenticate , login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import UserProfileForm
# Fatima 
from django.conf import settings
from friend.friend_request_status import FriendRequestStatus
from friend.models import FriendList, FriendRequest
from friend.utils import get_friend_request_or_false
from django.contrib.auth.decorators import login_required




# Create your views here.
def index(request):
    query=request.GET.get('q','')
    if(query):
        first_name_query1=User.objects.filter(first_name__contains=str(query))
        first_name_query2=User.objects.filter(first_name__in=[query])
        last_name_query1=User.objects.filter(last_name__contains=str(query))
        last_name_query2=User.objects.filter(last_name__in=[query])
        users = first_name_query1.union(first_name_query1,last_name_query1,last_name_query2)
        return render(request,"searchResult.html",{
            "usersResult":users,
        })
    users=User.objects.all()

    return render(request,"searchResult.html",{
        
        "usersResult":users,

    })

def signup(request):
    form = UserCreationForm(request.POST or None) 
    profile_form = UserProfileForm(request.POST,request.FILES or None)

    if form.is_valid() and profile_form.is_valid():
            form.save()

            profile = profile_form.save(commit = False)
          
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username , password=password)
            profile.user = user
            profile.save()
            if user:
                login(request , user)
                return redirect("/posts/")
            
    context = {'profile_form' : profile_form ,'form' : form }
    return render(request , "registration/signup.html", context)

def profile(request,id):
    context ={}
    account= User.objects.get(id=id)
    if  account:
        context['id'] = account.id
        context['username'] = account.username
        context['email'] = account.email
        context['avatar'] = account.userprofile.avatar
        #context['location'] = account.userprofile.location
        #context['age'] = account.userprofile.age

    try:
            friend_list = FriendList.objects.get(user=account)
    except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
    friends = friend_list.friends.all()
    context['friends'] = friends

    #define template variables
    is_self = True
    is_friend = False
    request_sent =  FriendRequestStatus.NO_REQUEST_SENT.value # range: ENUM -> friend/friend_request_status.FriendRequestStatus
    friend_requests = None
    user = request.user #authenticated user 
    if user.is_authenticated and user != account:
        is_self = False
        if friends.filter(pk=user.id):
            is_friend = True
        else:
            is_friend = False
            # CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
            if get_friend_request_or_false(sender=account, receiver=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
            # CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
            elif get_friend_request_or_false(sender=user, receiver=account) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
            # CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
                
    elif not user.is_authenticated:
            is_self = False
    else:
        try:
            is_self = True
            # You look at your own profile
            friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
        except:
            pass

    # Set the template variables to the values
    context['is_self'] = is_self
    context['is_friend'] = is_friend
    context['request_sent'] = request_sent
    context['friend_requests'] = friend_requests
    #context['BASE_URL'] = settings.BASE_URL
    #return render(request, "profile.html", context)
    return render(request, "profile.html",{
       "user":user,
       "account":account,
       "checker":context
   })

   # return render(request,'profile.html',{
   #     "user":user,
   # })

def about(request,id):
    user = User.objects.get(pk=id)
    return render(request,'about.html',{
        "user":user,
    })
def edit(request, id):
    user = User.objects.get(pk=id)
    form = UserCreationForm(request.POST or None, instance=user)
    profile_form = UserProfileForm(request.POST,request.FILES or None, instance=user)

    if form.is_valid() and profile_form.is_valid():
        form.save()
        profile = profile_form.save(commit = False)
        profile.user = user
        profile.save()
        return redirect('index')
    return render(request, 'accounts/edit.html', {
        'form': form,
        'profile':profile_form,
        'user': user
    })

@login_required(login_url="/login")
def userProfile(request):
    user=User.objects.get(pk=request.user.id)
    return render(request,'profile.html',{
        "user":user,
    })

