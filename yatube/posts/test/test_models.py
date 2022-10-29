from django.test import TestCase

from ..models import Group, Post, User, Comment


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст'
        )

    def test_post_model_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))

    def test_group_model_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))
