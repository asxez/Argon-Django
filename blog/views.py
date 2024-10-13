from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from pure_pagination.mixins import PaginationMixin

from .models import Post, Category, Tag


class BaseView(ListView):
    model = Post
    template_name = 'sim/index.html'
    context_object_name = 'post_list'

    def get_template_names(self):
        if self.__class__.__name__.startswith('Argon'):
            return ['argon/index.html']
        return [self.template_name]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['post_count'] = Post.objects.count()
        context['category_count'] = Category.objects.count()
        context['tag_count'] = Tag.objects.count()
        return context


class SimIndexView(PaginationMixin, BaseView):
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.all().order_by('-created_time')


class SimDetailView(DetailView):
    model = Post
    template_name = 'sim/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = super().get_object()
        post.add_views()
        return post


class SimArchivesView(BaseView):
    def get_queryset(self):
        return super().get_queryset().filter(
            created_time__year=self.kwargs.get('year'),
            created_time__month=self.kwargs.get('month')
        ).order_by('-created_time')


class SimCategoryView(PaginationMixin, BaseView):
    paginate_by = 10

    def get_queryset(self):
        categories = get_object_or_404(Category, name=self.kwargs.get('name'))
        return super().get_queryset().filter(category=categories).order_by('-created_time')


class SimTagView(BaseView):
    paginate_by = 10

    def get_queryset(self):
        tags = get_object_or_404(Tag, name=self.kwargs.get('name'))
        return super().get_queryset().filter(tags=tags).order_by('-created_time')


class NSearchView(PaginationMixin, SearchView):
    template_name = 'search/search_sim.html'
    queryset = SearchQuerySet().all()
    paginate_by = 10

    def get_template_names(self):
        path = self.request.path
        if 'argon' in path:
            return ['search/search_argon.html']
        return [self.template_name]

    def get_queryset(self):
        queryset = super().get_queryset().all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(content=query).order_by('-top', '-created_time')
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        if self.get_template_names() == ['search/search_argon.html']:
            context['page_information_show'] = True
            context['type'] = '搜索'
            context['name'] = self.request.GET.get('q', '未知查询')
            context['num'] = self.get_queryset().count()
            context['post_count'] = Post.objects.count()
            context['category_count'] = Category.objects.count()
            context['tag_count'] = Tag.objects.count()
            return context
        return context


class ArgonIndexView(PaginationMixin, BaseView):
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['show_toc_top'] = False
        context['body_class'] = 'home blog'
        context['main_class'] = 'article-list article-list-home'
        return context

    def get_queryset(self):
        return super().get_queryset().all().order_by('-top', '-created_time')


class ArgonDetailView(DetailView):
    model = Post
    template_name = 'argon/detail.html'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['post_count'] = Post.objects.count()
        context['category_count'] = Category.objects.count()
        context['tag_count'] = Tag.objects.count()

        context['show_toc_top'] = True
        context[
            'body_class'] = f'post-template-default single single-post postid-{self.kwargs.get("pk")} single-format-standard'
        context['main_class'] = ''
        return context

    def get_object(self, queryset=None):
        post = super().get_object()
        post.add_views()
        return post


class ArgonArchiveView(ListView):
    model = Post
    template_name = 'argon/archive.html'
    context_object_name = 'post_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['show_toc_top'] = True
        context['main_class'] = ''
        context['post_count'] = Post.objects.count()
        context['category_count'] = Category.objects.count()
        context['tag_count'] = Tag.objects.count()
        return context

    def get_queryset(self):
        return super().get_queryset().all()


class ArgonAllTagView(ListView):
    model = Tag
    template_name = 'argon/tag.html'
    context_object_name = 'tag_list'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['post_count'] = Post.objects.count()
        context['category_count'] = Category.objects.count()
        context['tag_count'] = Tag.objects.count()
        return context

    def get_queryset(self):
        return super().get_queryset().all()


class ArgonCategoryView(PaginationMixin, BaseView):
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['page_information_show'] = True
        context['type'] = '分类'
        context['name'] = self.kwargs.get('name')
        context['num'] = self.get_queryset().count()
        return context

    def get_queryset(self):
        category = get_object_or_404(Category, name=self.kwargs.get('name'))
        return super().get_queryset().filter(category=category).order_by('-top', '-created_time')


class ArgonTagView(PaginationMixin, BaseView):
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['page_information_show'] = True
        context['type'] = '标签'
        context['name'] = self.kwargs.get('name')
        context['num'] = self.get_queryset().count()
        return context

    def get_queryset(self):
        tag = get_object_or_404(Tag, name=self.kwargs.get('name'))
        return super().get_queryset().filter(tags=tag).order_by('-top', '-created_time')
