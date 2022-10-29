from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.public_link = [
            (
                reverse('posts:index'),
                'posts/index.html'
            ),
            (
                reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
                'posts/group_list.html'
            ),
            (
                reverse(
                    'posts:profile', kwargs={'username': cls.user.username}
                ),
                'posts/profile.html'
            ),
            (
                reverse('posts:post_detail', kwargs={'post_id': cls.post.id}),
                'posts/post_detail.html'
            )
        ]
        cls.private_link = [
            (
                reverse('posts:post_edit', args=[cls.post.id]),
                'posts/post_create.html'
            ),
            (
                reverse('posts:post_create'),
                'posts/post_create.html'
            ),
        ]

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_get_not_found(self):
        """Тест для не существующей страници."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_page_404_not_found(self):
        """Страница 404 отдаёт кастомный шаблон."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_edit_list_url_redirect_anonymous_on_login(self):
        """Страница по адресу posts/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/'
        )

    def test_create_list_url_redirect_anonymous_on_login(self):
        """Страница по адресу create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get(
            '/create/', follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_private_link_template(self):
        """Проверка шаблонов приватных страниц."""
        for url, template in self.private_link:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_public_link_template(self):
        """Проверка статуса публичных адресов гостем."""
        for url, template in self.public_link:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_private_link_status_code(self):
        """Проверка статуса публичных адресов гостем."""
        for url, _ in self.private_link:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_link_status_code(self):
        """Проверка статуса публичных адресов гостем."""
        for url, _ in self.public_link:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
