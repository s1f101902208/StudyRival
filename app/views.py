from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from .models import Record
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from django.db.models import Q, Sum

from .forms import PostForm
from django.conf import settings

import tweepy
import math

def login_form(request):
    return render(request, 'app/login.html', {})

def timer(request):
    if request.method=="POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect("mypage")
    form = PostForm() 
    records = Record.objects.all()
    return render(request, 'app/timer.html' , {'records': records, 'form': form, })

def mypage(request):
    q = User.objects.filter(id=request.user.id).annotate(times=Sum('record__time'))
    time = q[0].times
    if not time:
        time = 0
    lv = int(math.sqrt(time/3600) + 1)
    return render(request, 'app/info.html' , {'time': time_format(time), 'level': lv })

def ranking(request):
    # 各種キーをセット
    consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
    consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
    access_token = UserSocialAuth.objects.get(user__id=request.user.id).access_token.get('oauth_token')
    access_token_secret = UserSocialAuth.objects.get(user__id=request.user.id).access_token.get('oauth_token_secret')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
 
    # tweepy初期化
    api = tweepy.API(auth)
    my_info = api.me()
 
    friends_ids = []
    # フォローした人のIDを全取得
 
    # Cursor使うとすべて取ってきてくれるが，配列ではなくなるので配列に入れる
    try:
        for friend_id in tweepy.Cursor(api.friends_ids, user_id=my_info.id).items():
            friends_ids.append(friend_id)
 
        data = User.objects.filter(Q(social_auth__uid__in=friends_ids)| Q(id=request.user.id)).values('first_name').annotate(times=Sum('record__time')).order_by('-times')
        for i in range(len(data)):
            data[i]['times'] = time_format(data[i]['times'])
        return render(request, 'app/ranking.html', {'data': data})
    except:
        msg = "フォロー情報の取得に失敗しました"
        return render(request, 'app/ranking.html', {'error': msg,}) 
 
def time_format(time):
    if not time:
        return "00:00:00"
    h = time//3600
    m = time//60%60
    s = time%60
    return "%02d:%02d:%02d" % (h, m, s)
