from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, Follow


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username='test-username',
            first_name='Имя',
            last_name='Фамилия'
        )
        User.objects.create(
            username='followed',
            first_name='Любимый',
            last_name='Автор'
        )
        Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            text='Тестовый пост в группе',
            author=User.objects.get(pk=1),
            group=Group.objects.get(pk=1),
            image=uploaded,
            image_name='small.gif'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='notADog')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(User.objects.get(pk=1))


class PostViewHomepageTest(PostViewTests):
    def test_homepage_uses_correct_template(self):
        response = self.guest_client.get(reverse('index'))
        self.assertTemplateUsed(response, 'index.html')

    def test_homepage_shows_correct_content(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.context.get('page')[0].text, 'Тестовый пост в группе')
        self.assertEqual(response.context.get('page')[0].author.get_full_name(), 'Имя Фамилия')
        self.assertEqual(response.context.get('page')[0].image_name, 'small.gif')

    def test_homepage_shows_10_posts(self):
        for n in range(1, 11):
            Post.objects.create(
                text='A lot of posts',
                author=User.objects.get(pk=1)
            )
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(len(response.context['page']), 10)


class PostViewGroupPage(PostViewTests):
    def test_group_page_uses_correct_template(self):
        response = self.guest_client.get(reverse('group', kwargs={'slug': 'test-slug'}))
        self.assertTemplateUsed(response, 'group.html')

    def test_group_page_shows_correct_content(self):
        response = self.guest_client.get(reverse('group', kwargs={'slug': 'test-slug'}))
        self.assertEqual(response.context.get('page')[0].text, 'Тестовый пост в группе')
        self.assertEqual(response.context.get('page')[0].author.get_full_name(), 'Имя Фамилия')
        self.assertEqual(response.context.get('page')[0].image_name, 'small.gif')

    def test_group_post_appears_on_main_page(self):
        response = self.guest_client.get(reverse('index'))
        posts = response.context.get('page')
        group_post_exists = False
        for post in posts:
            if post.group:
                group_post_exists = True
        self.assertEqual(group_post_exists, True)

    def test_group_post_appears_on_group_page(self):
        response = self.guest_client.get(reverse('group', kwargs={'slug': 'test-slug'}))
        posts = response.context.get('page')
        group_post_exists = False
        for post in posts:
            if post.text == 'Тестовый пост в группе':
                group_post_exists = True
        self.assertEqual(group_post_exists, True)

    def test_group_post_on_wrong_group_page(self):
        Group.objects.create(
            title='Заголовок',
            slug='slug',
            description='другая группа'
        )
        response = self.guest_client.get(reverse('group', kwargs={'slug': 'slug'}))
        posts = response.context.get('page')
        group_post_exists = False
        if len(posts):
            for post in posts:
                if post.text == 'Тестовый пост в группе':
                    group_post_exists = True
        self.assertEqual(group_post_exists, False)


class PostViewProfilePage(PostViewTests):
    def test_profile_page_shows_correct_content(self):
        response = self.guest_client.get(reverse('profile', kwargs={'username': 'test-username'}))
        self.assertEqual(response.context.get('author').get_full_name(), 'Имя Фамилия')
        self.assertEqual(response.context.get('author').username, 'test-username')
        self.assertEqual(response.context.get('page')[0].text, 'Тестовый пост в группе')
        self.assertEqual(response.context.get('page')[0].image_name, 'small.gif')


class PostViewCreatePostTest(PostViewTests):
    def test_new_post_uses_correct_template(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertTemplateUsed(response, 'new_post.html')

    def test_new_post_shows_correct_content(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.ModelChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostViewPostTest(PostViewTests):
    def test_post_page_shows_correct_content(self):
        response = self.guest_client.get(reverse('post', kwargs={'username': 'test-username', 'post_id': 1}))
        self.assertEqual(response.context.get('author').get_full_name(), 'Имя Фамилия')
        self.assertEqual(response.context.get('author').username, 'test-username')
        self.assertEqual(response.context.get('post').text, 'Тестовый пост в группе')
        self.assertEqual(response.context.get('post').image_name, 'small.gif')


class PostViewEditTest(PostViewTests):
    def test_edit_page_shows_correct_content(self):
        response = self.authorized_author.get(reverse('post_edit', kwargs={'username': 'test-username', 'post_id': 1}))
        form_fields = {
            'group': 1,
            'text': 'Тестовый пост в группе'
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form')[value].value()
                self.assertEqual(form_field, expected)


class PostViewFollowPage(PostViewTests):
    def test_followers_see_new_post(self):
        Follow.objects.create(
            user=User.objects.get(pk=1),
            author=User.objects.get(pk=2)
        )
        Post.objects.create(
            text='Пост для читателей',
            author=User.objects.get(pk=2)
        )
        response = self.authorized_author.get('/follow/')
        self.assertEqual(response.context.get('page')[0].text, 'Пост для читателей')

    def test_unfollowers_dont_see_new_post(self):
        Post.objects.create(
            text='Пост для читателей',
            author=User.objects.get(pk=2)
        )
        response = self.authorized_client.get('/follow/')
        self.assertEqual(len(response.context.get('page')), 0)
