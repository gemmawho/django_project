from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(
            username='test-username',
            first_name='Имя',
            last_name='Фамилия'
        )
        Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Тестовый пост',
            author=User.objects.get(pk=1)
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username='NotACat')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(User.objects.get(pk=1))


class PostURLHomepageTest(PostURLTests):
    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        response = self.guest_client.get('/')
        self.assertTemplateUsed(response, 'index.html')


class PostURLGroupTest(PostURLTests):
    def test_group_page(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_group_page_uses_correct_template(self):
        response = self.guest_client.get('/group/test-slug/')
        self.assertTemplateUsed(response, 'group.html')


class PostURLProfileTest(PostURLTests):
    def test_profile_page(self):
        response = self.authorized_client.get('/test-username/')
        self.assertEqual(response.status_code, 200)

    def test_profile_page_for_guest(self):
        response = self.guest_client.get('/guest/')
        self.assertEqual(response.status_code, 404)

    def test_profile_page_for_authorized(self):
        response = self.authorized_client.get('/NotACat/')
        self.assertEqual(response.status_code, 200)


class PostURLPostTest(PostURLTests):
    def test_post_page(self):
        response = self.guest_client.get('/test-username/1/')
        self.assertEqual(response.status_code, 200)


class PostURLCreatePostTest(PostURLTests):
    def test_new_post(self):
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_uses_correct_template(self):
        response = self.authorized_client.get('/new/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_new_post_redirects_anonymous(self):
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_new_post_for_anonymous(self):
        response = self.guest_client.get('/new/')
        self.assertEqual(response.status_code, 302)


class PostURLEditTest(PostURLTests):
    def test_edit_page_for_anonymous(self):
        response = self.guest_client.get('/test-username/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_page_for_authorized(self):
        response = self.authorized_client.get('/test-username/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_page_for_author(self):
        response = self.authorized_author.get('/test-username/1/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_post.html')

    def test_edit_page_redirects_anonymous(self):
        response = self.guest_client.get('/test-username/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/test-username/1/edit/')

    def test_edit_page_redirects_authorized(self):
        response = self.authorized_client.get('/test-username/1/edit/', follow=True)
        self.assertRedirects(response, '/test-username/1/')


class PostURLFollow(PostURLTests):
    def test_authorized_can_follow(self):
        response = self.authorized_client.get('/test-username/follow/')
        self.assertRedirects(response, '/test-username/')

    def test_guest_cannot_follow(self):
        response = self.guest_client.get('/test-username/follow/')
        self.assertRedirects(response, '/auth/login/?next=/test-username/follow/')


class PostURLUnfollow(PostURLTests):
    def test_authorized_can_unfollow(self):
        response = self.authorized_client.get('/test-username/unfollow/')
        self.assertRedirects(response, '/test-username/')

    def test_guest_cannot_unfollow(self):
        response = self.guest_client.get('/test-username/unfollow/')
        self.assertRedirects(response, '/auth/login/?next=/test-username/unfollow/')


class PostURLCommentPage(PostURLTests):
    def test_guest_cannot_comment(self):
        response = self.guest_client.get('/test-username/1/comment/')
        self.assertRedirects(response, '/auth/login/?next=/test-username/1/comment/')

    def test_authorized_can_comment(self):
        response = self.authorized_client.get('/test-username/1/comment/')
        self.assertEqual(response.status_code, 200)


class PostURLNotFound(PostURLTests):
    def test_not_found_page(self):
        response = self.guest_client.get('/not-found/')
        self.assertEqual(response.status_code, 404)
