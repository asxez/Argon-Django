from django import template
from django.db.models.aggregates import Count

from ..models import Post, Category, Tag

register = template.Library()


@register.inclusion_tag('sim/include/recent_posts.html', takes_context=True)
def recent_posts(context, num=8):
    return {
        'recent_posts': Post.objects.all().order_by('-created_time')[:num]
    }


@register.inclusion_tag('sim/include/archives.html', takes_context=True)
def archives(context):
    return {
        'date_list': Post.objects.datetimes('created_time', 'month', order='DESC')
    }


@register.inclusion_tag('sim/include/category.html', takes_context=True)
def category_list(context):
    _category_list = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'category_list': _category_list
    }

@register.inclusion_tag('argon/include/category.html', takes_context=True)
def argon_category_list(context):
    _category_list = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'category_list': _category_list
    }


@register.inclusion_tag('sim/include/tag.html', takes_context=True)
def tags(context):
    return {
        'tags': Tag.objects.all()
    }

@register.inclusion_tag('argon/include/tag.html', takes_context=True)
def argon_tags(context):
    _tags = Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    return {
        'tags': _tags
    }
