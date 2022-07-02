
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pic')
    bio = models.TextField(max_length=170, blank=True, null=True)
    cover_pic = models.ImageField(upload_to='cover_pic', blank=True)

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'profile_pic': self.profile_pic.url,
            'first_name':self.first_name,
            'last_name': self.last_name
        }

class Post(models.Model):
    creater = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    date_created = models.DateTimeField(default=timezone.now)
    content_text  = models.TextField(max_length=200, blank=True)
    content_image = models.ImageField(upload_to='posts', blank=True)
    likers = models.ManyToManyField(User, blank=True, related_name='likes')
    savers = models.ManyToManyField(User, blank=True, related_name='saved')
    comment_count = models.IntegerField(default=0)

    def __str__(self):
        return f"POST ID:{self.id} (creater: {self.creater})"

    def img_url(self):
        return self.content_image.url

    def append(self , name , value):
        self.name = value

class Comment(models.Model):
    post = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commenters')
    comment_content = models.TextField(max_length=200)
    comment_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Post: {self.post} | Post_id: {self.post.id} | commenter: {self.commenter}"

    def serialize(self):
        return {
            "id": self.id,
            "commenter": self.commenter.serialize(),
            "body": self.comment_content,
            "timestamp": self.comment_time.strftime("%b %d %Y, %I:%M %p")
        }


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    followers = models.ManyToManyField(User, blank=True, related_name='following')

    def __str__(self):
        return f"User: {self.user} | followers:{self.followers.count()} "
    
    