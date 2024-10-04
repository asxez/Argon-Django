import random
import re

import markdown
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension


class Category(models.Model):
    """分类"""
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    """标签"""
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


def generate_md(string):
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.fenced_code',
        'markdown.extensions.toc',
        TocExtension(slugify=slugify)
    ])

    have_doc = re.findall(r'\[TOC]', string, re.S)
    content = md.convert(string)
    toc = md.toc if len(have_doc) != 0 else ''
    content = re.sub(r'(^<div class="toc">.*?</div>)', '', content, re.S)
    return {'content': content, 'toc': toc}


class Post(models.Model):
    """文章的数据库表"""
    title = models.CharField('标题', max_length=70)
    body = models.TextField('正文')

    created_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateTimeField('修改时间')

    excerpt = models.CharField('摘要', max_length=200, blank=True)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    author = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)

    views = models.PositiveIntegerField(default=0, editable=False)

    img = models.ImageField(upload_to='images/', verbose_name='图片', default='', blank=True)
    top = models.BooleanField(default=False, verbose_name='是否置顶')

    word_count = models.PositiveIntegerField(default=0, editable=False)
    reading_time = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.modified_time = timezone.now()
        md = markdown.Markdown(extensions=['markdown.extensions.extra'])
        convert = md.convert(str(self.body))
        self.excerpt = strip_tags(convert)[:100]
        self.word_count = len(strip_tags(convert))
        self.reading_time = round(int(self.word_count) / 250)
        super().save(*args)

    def get_absolute_url(self):
        """same as {% url 'blog:detail' post.pk %}"""
        return reverse('blog:sim_detail', kwargs={'pk': self.pk})

    def get_absolute_url_argon(self):
        return reverse('blog:argon_detail', kwargs={'pk': self.pk})

    def add_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    @cached_property
    def md(self):
        return generate_md(self.body)

    @property
    def toc(self):
        return self.md.get('toc', '')

    @property
    def body_html(self):
        return self.md.get('content', '')

    # 获取上一篇文章
    def get_previous_post(self):
        return Post.objects.filter(created_time__lt=self.created_time).order_by('-created_time').first()

    # 获取下一篇文章
    def get_next_post(self):
        return Post.objects.filter(created_time__gt=self.created_time).order_by('created_time').first()

    # 文章推荐，在同一个分类下推荐文章
    def get_recommended_posts(self):
        recommended_posts = Post.objects.filter(category=self.category).exclude(pk=self.pk)
        if recommended_posts.count() >= 4:
            return random.sample(list(recommended_posts), 4)  # 随机选择4篇文章
        return recommended_posts
