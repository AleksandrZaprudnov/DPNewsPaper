from django.forms import DateInput, ModelForm
from django_filters import CharFilter
from .models import Post


class DateInputWidget(DateInput):
    input_type = 'date'


class NewsModelForm(ModelForm):

    post_news = 'PN'
    post_article = 'PA'

    TYPE_POST = [
        (post_news, 'Новость'),
        (post_article, 'Статья'),
    ]

    type_post = CharFilter(field_name='type_post', max_length=2, choices=TYPE_POST, blank=False, default=post_news)

    class Meta:
        model = Post

        fields = ['author', 'type_post', 'title', 'categories', 'text_article']

