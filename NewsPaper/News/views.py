from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from datetime import datetime
from .models import Post, User, Category, MailingLists
from .filters import NewsFilter, NewsFilterByCategory
from .forms import NewsModelForm


class PostsListView(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-datetime_created')
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostsSearchList(ListView):
    model = Post
    template_name = 'news/search/posts_list.html'
    context_object_name = 'posts'
    ordering = '-datetime_created'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered = NewsFilter(self.request.GET, queryset=self.get_queryset())
        context['filter'] = filtered

        paginated_filtered_persons = Paginator(filtered.qs, self.paginate_by)
        page_number = self.request.GET.get('page')
        person_page_object = paginated_filtered_persons.get_page(page_number)
        context['person_page_object'] = person_page_object

        return context


class PostsSearchByCategoryList(ListView):
    model = Post
    template_name = 'news/search/posts_list_category.html'
    context_object_name = 'posts'
    ordering = '-datetime_created'
    paginate_by = 10
    signed = False

    def post(self, request, *args, **kwargs):
        if request.POST['category_objects']:
            email_list = [
                request.user.email,
            ]
            user_profile = User.objects.get(user_django=request.user)
            category = Category.objects.get(pk=request.POST['category_objects'])
            subscriptions = MailingLists.objects.filter(user=user_profile, category=category)

            if not subscriptions.exists():
                subscription = MailingLists(
                    user=user_profile,
                    category=category,
                )
                subscription.save()

                html_content = render_to_string(
                    'news/subscription_created.html',
                    {
                        'subscription': subscriptions.first(),
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=f'Новостной портал News paper: Вы подписаны {datetime.utcnow().strftime("%d/%m/%y %H:%M")}',
                    from_email='a.zaprudnov@abbott.ru',
                    to=email_list,
                )
                msg.attach_alternative(html_content, "text/html")

                msg.send()
            else:
                self.signed = True

        return redirect('post_searchbycategory')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered = NewsFilterByCategory(self.request.GET, queryset=self.get_queryset())
        context['filter'] = filtered

        paginated_filtered_persons = Paginator(filtered.qs, self.paginate_by)
        page_number = self.request.GET.get('page')
        person_page_object = paginated_filtered_persons.get_page(page_number)
        context['person_page_object'] = person_page_object
        context['signed'] = self.signed

        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'News.add_post'
    template_name = 'news/post_create.html'
    form_class = NewsModelForm


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'News.change_post'
    template_name = 'news/post_update.html'
    form_class = NewsModelForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'

