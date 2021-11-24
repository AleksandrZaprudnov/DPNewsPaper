import logging

from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.contrib.auth.models import User as UserDjango
from NewsPaper.News.models import Post
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    print('Posts in a week')
    # start_date = datetime.today() - timedelta(days=7)
    #
    # # Определение листа подписанных пользователей
    # list_users_id = []
    # subscriptions = MailingLists.objects.all()
    # for subscription in subscriptions:
    #     if not subscription.user_id in list_users_id:
    #         list_users_id.append(subscription.user_id)
    #
    # for user_id_ in list_users_id:
    #     users_django = UserDjango.objects.get(id=User.objects.get(pk=user_id_).user_django_id)
    #     subscriptions = MailingLists.objects.filter(user_id=user_id_)
    #
    #     for subscription in subscriptions:
    #         posts_categories = PostCategory.objects.filter(categories_id=subscription.category_id)
    #         category = Category.objects.get(id=subscription.category_id)
    #
    #         appeal = f'Категория {category}.'
    #
    #         for record in posts_categories:
    #             post = Post.objects.get(id=record.posts_id, datetime_created__gte=start_date)
    #
    #             body_text = f'{str(post.text_article)[:50]} ...'
    #             link = f'http://127.0.0.1:8000/news/{record.posts_id}'
    #
    #         html_content = render_to_string(
    #             'news/subscription_news_subscriptions.html',
    #             {
    #                 'appeal': appeal,
    #                 'body_text': body_text,
    #                 'link': link,
    #             }
    #         )
    #
    #         msg = EmailMultiAlternatives(
    #             subject=f'Новостной портал News paper: новая публикация',
    #             from_email='a....@....ru',
    #             to=[users_django.email],
    #         )
    #         msg.attach_alternative(html_content, "text/html")
    #         msg.send()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            # Каждую неделю 60*60*24*7
            trigger=CronTrigger(second="*/604800"),
            # trigger=CronTrigger(second="*/30"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить,
            # либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

