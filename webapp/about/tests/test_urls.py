from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech_page(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_template(self):
        template_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/'
        }
        for template, reserve_name in template_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reserve_name)
                self.assertTemplateUsed(response, template)
