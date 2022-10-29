import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.user_unfollower = User.objects.create_user(username='unfollower')
        cls.user_follower = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user_follower
        )
        cls.post_author = Post.objects.create(
            author=cls.author,
            text='Текс автора'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.user
        )
        cls.index_url = reverse(
            'posts:index'
        )
        cls.group_list = reverse(
            'posts:group_list', kwargs={'slug': 'test-slug'}
        )
        cls.profile = reverse(
            'posts:profile', kwargs={'username': 'test-user'}
        )
        cls.post_create = reverse(
            'posts:post_create'
        )
        cls.post_edit = reverse(
            'posts:post_edit', args=[cls.post.id]
        )
        cls.add_comment = reverse(
            'posts:add_comment', kwargs={'post_id': cls.post.id}
        )
        cls.post_detail = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.follow_index = reverse(
            'posts:follow_index'
        )
        cls.profile_follow = reverse(
            'posts:profile_follow', kwargs={'username': 'author'}
        )
        cls.profile_unfollow = reverse(
            'posts:profile_unfollow', kwargs={'username': 'author'}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.follower_client = Client()
        self.unfollower_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client.force_login(self.user_follower)
        self.unfollower_client.force_login(self.user_unfollower)

    def post_check(self, response_post):
        self.assertEqual(response_post.text, self.post.text)
        self.assertEqual(response_post.author, self.post.author)
        self.assertEqual(response_post.group, self.post.group)
        self.assertEqual(response_post.image, self.post.image)

    def group_check(self, response_group):
        self.assertEqual(response_group.title, self.group.title)
        self.assertEqual(response_group.slug, self.group.slug)

    def test_index_show_correct_context(self):
        """Тест корректность отобржения контекста для главной страницы."""
        response = self.guest_client.get(
            (self.index_url)
        )
        response_post = response.context.get('page_obj')[0]
        self.post_check(response_post)

    def test_index_page_cache(self):
        """Тест для проверки кэша на главной странице."""
        new_post = Post.objects.create(
            author=self.user,
            text='Пост для кеша'
        )
        response = self.authorized_client.get((self.index_url))
        new_post.delete()
        response_after_delete = self.authorized_client.get(
            (self.index_url)
        )
        self.assertEqual(response_after_delete.content, response.content)
        cache.clear()
        response_after_clear_cache = self.authorized_client.get(
            (self.index_url)
        )
        self.assertNotEqual(
            response_after_clear_cache.content, response.content
        )

    def test_group_list_correct_context(self):
        """Тест корректность отобржения контекста для группы."""
        response = self.guest_client.get(
            (self.group_list)
        )
        context = response.context
        response_post = context.get('page_obj')[0]
        response_group = context.get('group')
        self.post_check(response_post)
        self.group_check(response_group)

    def test_post_detail_correct_context(self):
        """Тест корректности контекста для post_detail."""
        response = self.authorized_client.get(
            (self.post_detail)
        )
        context = response.context
        response_post = context.get('post')
        response_comment = context.get('comments')[0]
        self.post_check(response_post)
        self.assertEqual(response_comment.post, self.post)
        self.assertEqual(response_comment.author, self.user)
        self.assertEqual(response_comment.text, self.comment.text)

    def test_profile_correct_context(self):
        """Тест корректность отобржения контекста для профиля автора."""
        response = self.guest_client.get(
            (self.profile)
        )
        context = response.context
        response_post = context.get('page_obj')[0]
        response_author = context.get('author')
        self.post_check(response_post)
        self.assertEqual(response_author.username, self.user.username)

    def test_post_edit_correct_context(self):
        """Тест корректность отобржения контекста для редактирование поста."""
        response = self.authorized_client.get(
            (self.post_edit)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        """Тест корректность отобржения контекста для создания поста."""
        response = self.authorized_client.get(
            (self.post_create)
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_page_display(self):
        view_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': 'test-user'}
            )
        ]
        for view_name in view_names:
            with self.subTest(view_name=view_name):
                response = self.authorized_client.get(view_name)
                self.assertIn('page_obj', response.context)
                self.assertEqual(response.context.get(
                    'page_obj')[0], self.post
                )

    def test_unfollower_client_can_follow_to_author(self):
        """Пользователь может подписаться на автора."""
        self.unfollower_client.get(
            (self.profile_follow)
        )
        follow = Follow.objects.filter(
            user=self.user_unfollower,
            author=self.author
        )
        self.assertTrue(follow.exists())

    def test_follower_client_cannt_unfollow_from_author(self):
        """Пользователь может отписаться от автора."""
        self.follower_client.get(
            (self.profile_unfollow)
        )
        follow = Follow.objects.filter(
            user=self.user_follower,
            author=self.author
        )
        self.assertFalse(follow.exists())

    def test_post_add_in_page_for_follow_client(self):
        """Запись пользователя появляется в ленте тех, кто на него подписан."""
        Follow.objects.get_or_create(
            user=self.user_follower,
            author=self.author
        )
        response = self.follower_client.get(
            (self.follow_index)
        )
        response_post = (
            response.context.get('page_obj').paginator.object_list.filter(
                author=self.author
            )
        )
        self.assertTrue(response_post.exists())

    def test_post_not_add_page_in_unfollow_client(self):
        """Запись пользователя  не появляется в ленте тех,
           кто на него не подписан.
        """
        Follow.objects.filter(
            user=self.user_unfollower,
            author=self.author
        ).delete()
        response = self.unfollower_client.get(
            (self.follow_index)
        )
        response_post = (
            response.context.get('page_obj').paginator.object_list.filter(
                author=self.author
            )
        )
        self.assertFalse(response_post.exists())
