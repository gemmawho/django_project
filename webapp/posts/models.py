from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()
# Create your models here.


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    objects = (title, slug, description)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст', help_text='Напишите то, что у вас на душе')
    pub_date = models.DateTimeField('date published', auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Группа',
                              help_text='Выберите группу по желанию')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    image_name = models.CharField(max_length=100, blank=True, null=True)
    objects = (text, pub_date, author, group, image, image_name)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    objects = (post, author, text, created)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='following', null=True, on_delete=models.CASCADE)
    objects = (user, author)

    def __str__(self):
        return self.author