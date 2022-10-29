from django.test import TestCase
from django.urls import reverse

from ..models import Post, User
from ..util import LIMIT


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nikita')
        new_posts = [
            Post(
                author=cls.user,
                text='Test' + str(i)
            ) for i in range(LIMIT + 1)
        ]
        Post.objects.bulk_create(new_posts)

    def test_page_contains_records(self):
        """Проверка: количество постов на странице."""
        posts_count = Post.objects.count()
        pots_left = posts_count - LIMIT
        view_names = [(1, LIMIT), (2, pots_left)]
        for page, posts in view_names:
            with self.subTest(page=page):
                response = self.client.get(
                    reverse('posts:index'), {'page': page}
                )
                self.assertEqual(len(response.context['page_obj']), posts)
