from datetime import datetime, timedelta
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User as UserDjango
from django.template.loader import render_to_string
from .models import Post, PostCategory, Category, MailingLists, User


# celery -A app_my worker -l INFO -B
# Флаг B - периодические задачи

@shared_task
def send_mail(user_email, html_content):
    print(f'Отправка уведомления для: {user_email}')

    msg = EmailMultiAlternatives(
        subject=f'Новостной портал News paper: новая публикация',
        from_email='a....@....ru',
        to=[user_email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def news_week():
    print('Отправка новостей за неделю')

    qs_categories_id = PostCategory.objects.filter(
        posts_id__datetime_created__gte=datetime.utcnow() - timedelta(7)
    ).values('categories_id')

    list_id = []
    for category_id in qs_categories_id:
        if not category_id['categories_id'] in list_id:
            list_id.append(category_id['categories_id'])

    for id_c in list_id:
        list_users_id = []
        subscriptions = MailingLists.objects.filter(category_id=id_c)
        for subscription in subscriptions:
            if not subscription.user_id in list_users_id:
                list_users_id.append(subscription.user_id)

        users = User.objects.filter(id__in=list_users_id).values('user_django_id')
        users_django = UserDjango.objects.filter(id__in=users)

        for user in users_django:
            appeal = f'Уважаемый {user} Вы подписаны на категории (см. ниже), есть новые публикации за неделю.'

            posts = PostCategory.objects.filter(categories_id=id_c).values('posts_id')

            body_text = ''
            for id_p in posts:
                print(Post.objects.get(pk=id_p["posts_id"]).title)
                body_text += f'{str(Post.objects.get(pk=id_p["posts_id"]).text_article)[:50]} ...<br>'
                body_text += f'http://127.0.0.1:8000/news/{Post.objects.get(pk=id_p["posts_id"]).id}<br>'

            comments = f'Категория {Category.objects.get(pk=id_c).name}'

            html_content = render_to_string(
                'news/subscription_news_week.html',
                {
                    'appeal': appeal,
                    'body_text': body_text,
                    'comments': comments
                }
            )

            msg = EmailMultiAlternatives(
                subject=f'Новостной портал News paper: новости за неделю',
                from_email='a....@....ru',
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

