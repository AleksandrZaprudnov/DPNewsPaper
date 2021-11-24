from django_filters import FilterSet, DateFilter, CharFilter, ModelChoiceFilter
from .models import Post, Category
from .forms import DateInputWidget


class NewsFilter(FilterSet):

    title_icon = CharFilter(field_name='title', lookup_expr='icontains', label='Заголовок (сод.)')
    user_name_icon = CharFilter(field_name='author__users_id__name', lookup_expr='icontains', label='Имя польз. (сод.)')
    datetime_created__gte = DateFilter(field_name='datetime_created', lookup_expr='gte', label='Дата (>=)', widget=DateInputWidget)

    class Meta:

        model = Post

        fields = {
            # 'title': ['icontains'],
        }


class NewsFilterByCategory(FilterSet):

    category_objects = ModelChoiceFilter(field_name='categories', queryset=Category.objects.all(), label='Категория', )
    datetime_created__gte = DateFilter(field_name='datetime_created', lookup_expr='gte', label='Дата (>=)', widget=DateInputWidget)

    class Meta:

        model = Post

        fields = {
            # 'title': ['icontains'],
        }

