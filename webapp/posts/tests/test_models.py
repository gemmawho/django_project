from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Post, Group


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username='юзернейм')
        Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Тестовый пост',
            author=User.objects.get(pk=1),
            group=Group.objects.get(pk=1)
        )
        cls.post = Post.objects.get(pk=1)
        cls.group = Group.objects.get(pk=1)

    def test_post_verbose_name(self):
        post = PostModelTests.post
        self.assertEqual(post._meta.get_field('text').verbose_name, 'Текст')
        self.assertEqual(post._meta.get_field('group').verbose_name, 'Группа')

    def test_post_help_text(self):
        post = PostModelTests.post
        self.assertEqual(post._meta.get_field('text').help_text, 'Напишите то, что у вас на душе')
        self.assertEqual(post._meta.get_field('group').help_text, 'Выберите группу по желанию')

    def test_post_str(self):
        post = PostModelTests.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_str(self):
        group = PostModelTests.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
