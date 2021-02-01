from django.test import Client, TestCase
from django.urls import reverse


class AboutViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_use_correct_templates(self):
        templates_page_names = {
            'author.html': reverse('about:author'),
            'tech.html': reverse('about:tech')
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
