from django.db.models.signals import m2m_changed
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.contrib.auth.models import User as UserDjango
from .models import User, Post, MailingLists
from .tasks import send_mail


# sender - класс промежуточный (PostCategory)
# instance - изменяемый экземпляр (Post)
# model - класс добавленных объектов (Category)
@receiver(m2m_changed, sender=Post.categories.through)
def notify_users_posts_categories(sender, instance, action, model, pk_set, **kwargs):

    if action == 'post_add':
        list_id = []
        for el in pk_set:
            list_id.append(el)

        categories = sender.objects.filter(posts_id=instance.id, categories_id__in=list_id).values('categories_id')

        str_categories = ''
        list_id.clear()
        for category_id in categories:
            if str_categories:
                str_categories += ', '
            id_c = category_id['categories_id']
            list_id.append(id_c)
            str_categories += model.objects.get(pk=id_c).name

        list_users_id = []
        subscriptions = MailingLists.objects.filter(category_id__in=list_id)
        for subscription in subscriptions:
            if not subscription.user_id in list_users_id:
                list_users_id.append(subscription.user_id)

        users = User.objects.filter(id__in=list_users_id).values('user_django_id')
        users_django = UserDjango.objects.filter(id__in=users)

        for user in users_django:
            appeal = f'Уважаемый {user} Вы подписаны на категории (см. ниже), есть новая публикация.'
            body_text = f'{str(instance.text_article)[:50]} ...'
            comments = f'Категории:\n{str_categories}'
            link = f'http://127.0.0.1:8000/news/{instance.id}'

            html_content = render_to_string(
                'news/subscription_new_in_category.html',
                {
                    'appeal': appeal,
                    'body_text': body_text,
                    'comments': comments,
                    'link': link
                }
            )

            send_mail(user.email, html_content)

