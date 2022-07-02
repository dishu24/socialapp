
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import *

# Create your views here.

def home(request):
    return render(request,'login.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        profile = request.FILES.get('profile')
        cover = request.FILES.get('cover')

        password = request.POST['password']
        confirmation = request.POST['confirmation']
        context= {'username':username,'email':email,'firstname':fname,'lastname':lname,'password':password,'confirmation':confirmation}
        print(context)
        if password != confirmation:
            return render(request,'signup.html',{'msg':"password doesn't match."})
        
        try:
            user = User.objects.create_user(username,email,password)
            user.first_name=fname
            user.last_name=lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = 'static/noprofile.png'
            user.cover = cover
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request,'signup.html',{'message':'Username already exits.'})
        login(request,user)
        return redirect('login')
    return render(request, 'signup.html')

def loginuser(request):
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        print(username,".....",password)
        user = authenticate(username=username, password=password)
        if user.is_authenticated:
            print(user)
            login(request, user)
            return redirect('mainview')
       
        else:
            return render(request,'login.html',{'message':'Invalid username or password.'})
        
    else:
        return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect(("login"))

def mainview(request):
    all_posts = Post.objects.all().order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
    return render(request, "main.html", {
        "posts": posts,
        "suggestions": suggestions,
        "page": "all_posts",
        'profile': False
    })

def profile(request, username):
    user = User.objects.get(username=username)
    print(user)
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts,10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    
    posts = paginator.get_page(page_number)
    following=[]
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        following = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=following).exclude(username=request.user.username).order_by("?")[:6]

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True
        
        follower_count = Follower.objects.get(user=user).followers.all().count()
        following_count = Follower.objects.filter(followers=user).count()

    
    return render(request,'profile.html',{
        'username':user,
        'posts': posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count
        
        })

@csrf_exempt
@login_required
def follow(request,username):
    if request.user.is_authenticated:
        if request.method == "PUT":
            user = User.objects.get(username=username)
            print(user)
            print("follower",request.user)
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=240)
            except Exception as e:
                return HttpResponse(e)

@csrf_exempt
@login_required
def unfollow(request,username):
    if request.user.is_authenticated:
        if request.method == "PUT":
            user = User.objects.get(username=username)
            print(user)
            print("unfollower",request.user)
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=240)
            except Exception as e:
                return HttpResponse(e)


def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts,10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
    
        posts = paginator.get_page(page_number)
        following = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=following).exclude(username=request.user.username).order_by("?")[:6]

        return render(request,'main.html', {
            'posts':posts,
            'suggestions':suggestions,
            'page':"following"
        })

def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')
        paginator = Paginator(all_posts,10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        
        posts = paginator.get_page(page_number)
        following = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=following).exclude(username=request.user.username).order_by("?")[:6]

        return render(request,'main.html', {
            'posts':posts,
            'suggestions':suggestions,
            'page':"saved"
        })

@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            # print("post....saved",post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=240)
            except Exception as e:
                return HttpResponse(e)

@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            # print("post....unsaved",post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=240)
            except Exception as e:
                return HttpResponse(e)

@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            # print("post....like",post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=240)
            except Exception as e:
                return HttpResponse(e)

@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print("post....unlike",post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=240)
            except Exception as e:
                return HttpResponse(e)

def createpost(request):
    if request.method == "POST":
        text = request.POST.get('text')
        img = request.FILES.get('picture')
        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=img)
            return redirect('mainview')
        except Exception as e:
            return HttpResponse(e)

@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            post =Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delete_post= post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)

@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "POST":
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img-change')
        post_id = request.POST.get('id')
        print(post_id)
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()
            
            if(post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if(post.content_image):
                post_image = post.img_url()
            else:
                post_image = False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            print(e)
            print('--------')
            return JsonResponse({
                "success": False
            })

@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            comment = data.get('comment_text')
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(post=post,commenter=request.user,comment_content=comment)
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)
    
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))