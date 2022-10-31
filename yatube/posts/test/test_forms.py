import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group
        )
        cls.image_for_create = SimpleUploadedFile(
            name='small1.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.image_for_edit = SimpleUploadedFile(
            name='small2.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_form(self):
        """Тест на проверку создания записи в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тест прошёл успешно',
            'image': self.image_for_create,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        created_post = Post.objects.latest('pk')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(created_post.group.id, form_data['group'])
        self.assertEqual(created_post.author, self.user)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.image, 'posts/small1.gif')
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )

    def test_anonymous_not_create_post(self):
        """Тест анонимный пользователь не может создать пост."""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тест прошёл успешно',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_edit_form(self):
        """Тест для редактирование записи."""
        form_data = {
            'text': 'Редактированный текст',
            'group': self.group.id,
            'image': self.image_for_edit
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edit_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.id, form_data['group'])
        self.assertEqual(edit_post.image, 'posts/small2.gif')

    def test_authorized_client_add_comment(self):
        '''Авторизованный клиент может комментировать посты автора.'''
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        created_comment = Comment.objects.latest('pk')
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(created_comment.text, form_data['text'])
        self.assertEqual(created_comment.author, self.user)
        self.assertEqual(created_comment.post, self.post)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_guest_client_cannt_add_comment(self):
        """Не авторизованный клиент не может оставлять комментарии."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Комментарий'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/comment/'
        )
