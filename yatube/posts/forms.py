from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'group': 'Группа',
            'text': 'Сообщение'
        }
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Введите ссообщение'
        }
        fields = ('group', 'text', 'image')

        def clean_post(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError("Поле не заполнено!")
            return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
