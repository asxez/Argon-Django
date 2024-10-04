from haystack import indexes

from .models import Post


class PostSearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    content = indexes.CharField(model_attr='body')
    created_time = indexes.DateTimeField(model_attr='created_time')
    top = indexes.BooleanField(model_attr='top')

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
