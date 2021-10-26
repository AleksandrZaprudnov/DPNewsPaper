from django.db import models


post_news = 'PN'
post_article = 'PA'

TYPE_POST = [
    (post_news, 'Новость'),
    (post_article, 'Статья'),
]


# Модель User
# Модель, содержащая всех пользователей
# Имеет одно поле
# - имя пользователя.

class User(models.Model):
    name = models.CharField(max_length=255, null=False)


# Модель Author
# Модель, содержащая объекты всех авторов.
# Имеет следующие поля:
# cвязь - «один к одному» с встроенной моделью пользователей User;
# рейтинг - пользователя.
# Рейтинг надо посчитать.

class Author(models.Model):
    name = models.CharField(max_length=255, null=False)
    _rating = models.IntegerField(default=0, db_column="rating")
    users = models.OneToOneField("User", on_delete=models.CASCADE)

    # суммарный рейтинг каждой статьи автора умножается на 3;
    # суммарный рейтинг всех комментариев автора;
    # суммарный рейтинг всех комментариев к статьям автора.
    def update_rating(self):
        list_post = Post.objects.filter(author=self).values('_rating')
        sum_ = 0
        for el in list_post:
            sum_ = sum_ + int(el['_rating']) * 3

        list_comment = Comment.objects.filter(users=self.users).values('_rating')
        for el in list_comment:
            sum_ = sum_ + int(el['_rating'])

        list_comment_author = Comment.objects.filter(posts__in=Post.objects.filter(author=self)).values('_rating')
        for el in list_comment_author:
            sum_ = sum_ + int(el['_rating'])

        self._rating = sum_
        self.save()

# Модель Category
# Категории новостей / статей — темы,
# которые они отражают(спорт, политика, образование и т.д.).
# Имеет единственное поле: название категории.
# Поле должно быть уникальным.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)


# Модель Post
# Эта модель должна содержать в себе статьи и новости,
# которые создают пользователи. Каждый объект может иметь одну или несколько категорий.
# Соответственно, модель должна включать следующие поля:
# связь «один ко многим» с моделью Author;
# поле с выбором — «статья» или «новость»;
# автоматически добавляемая дата и время создания;
# связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory);
# заголовок статьи / новости;
# текст статьи / новости;
# рейтинг статьи / новости.

class Post(models.Model):
    author = models.ForeignKey("Author", on_delete=models.CASCADE, related_name="posts")
    type_post = models.CharField(max_length=2, choices=TYPE_POST, default=post_news)
    datetime_created = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField("Category", through="PostCategory")
    title = models.CharField(max_length=255, null=False)
    text_article = models.TextField(null=False)
    _rating = models.IntegerField(default=0, db_column="rating")

    @property
    def like(self):
        return self._rating

    @like.setter
    def like(self, value):
        self._rating += int(value)
        self.save()

    @property
    def dislike(self):
        return self._rating

    @dislike.setter
    def dislike(self, value):
        if (self._rating > 0) and (int(value) > self._rating):
            self._rating = 0
        else:
            self._rating -= int(value)

        self.save()

    def preview(self):
        return self.text_article[:124] + " ..."


# Модель PostCategory
# Промежуточная модель для связи «многие ко многим»:
# связь «один ко многим» с моделью Post;
# связь «один ко многим» с моделью Category.

class PostCategory(models.Model):
    posts = models.ForeignKey("Post", on_delete=models.CASCADE)
    categories = models.ForeignKey("Category", on_delete=models.CASCADE)


# Модель Comment
# Под каждой новостью / статьёй можно оставлять комментарии,
# поэтому необходимо организовать их способ хранения тоже.
# Модель будет иметь следующие поля:
# связь «один ко многим» с моделью Post;
# связь «один ко многим» со встроенной моделью
# User (комментарии может оставить любой пользователь, необязательно автор);
# текст комментария;
# дата и время создания комментария;
# рейтинг комментария.

class Comment(models.Model):
    posts = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    users = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments")
    text_comment = models.TextField(null=False)
    datetime_comment = models.DateTimeField(auto_now_add=True)
    _rating = models.IntegerField(default=0, db_column="rating")

    @property
    def like(self):
        return self._rating

    @like.setter
    def like(self, value):
        self._rating += int(value)
        self.save()

    @property
    def dislike(self):
        return self._rating

    @dislike.setter
    def dislike(self, value):
        if (self._rating > 0) and (int(value) > self._rating):
            self._rating = 0
        else:
            self._rating -= int(value)

        self.save()

