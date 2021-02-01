from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username='test-username')
        Group.objects.create(
            title='Заголовок',
            slug='slug',
            description='Описание'
        )
        Post.objects.create(
            text='Тестовый текст',
            author=User.objects.get(pk=1),
            group=Group.objects.get(pk=1)
        )
        cls.user = User.objects.get(pk=1)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_create_new_post(self):
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост',
            'author': 1,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_edit_existing_post(self):
        edit_data = {
            'group': 1,
            'text': 'Отредактированный пост'
        }
        response = self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'test-username', 'post_id': 1}),
            data=edit_data,
            follow=True
        )
        self.assertRedirects(response, '/test-username/1/')
        self.assertEqual(response.context.get('post').text, 'Отредактированный пост')

    def test_edited_post_on_homepage(self):
        edit_data = {
            'group': 1,
            'text': 'Отредактированный пост'
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'test-username', 'post_id': 1}),
            data=edit_data,
            follow=True
        )
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(response.context.get('page')[0].text, 'Отредактированный пост')

    def test_edited_post_on_group_page(self):
        edit_data = {
            'group': 1,
            'text': 'Отредактированный пост'
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'test-username', 'post_id': 1}),
            data=edit_data,
            follow=True
        )
        response = self.authorized_client.get(reverse('group', kwargs={'slug': 'slug'}))
        self.assertEqual(response.context.get('page')[0].text, 'Отредактированный пост')

    def test_post_group_after_edit(self):
        Group.objects.create(
            title='Новая группа',
            slug='edited-slug',
            description='новое описание'
        )
        edit_data = {
            'group': 2,
            'text': 'Отредактированный пост'
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'test-username', 'post_id': 1}),
            data=edit_data,
            follow=True
        )
        response_on_new_group = self.authorized_client.get(reverse('group', kwargs={'slug': 'edited-slug'}))
        response_on_old_group = self.authorized_client.get(reverse('group', kwargs={'slug': 'slug'}))
        self.assertEqual(response_on_new_group.context.get('page')[0].text, 'Отредактированный пост')
        self.assertEqual(response_on_old_group.context.get('page').paginator.count, 0)


