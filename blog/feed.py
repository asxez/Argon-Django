from django.contrib.syndication.views import Feed

from .models import Post


class RssFeed(Feed):
    title = 'blog_feed'
    link = '/'
    description = 'This is blog feed'

    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body_html
