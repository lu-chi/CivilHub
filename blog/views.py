# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.timesince import timesince
from django.views.generic import View, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.contenttypes.models import ContentType
from maps.forms import AjaxPointerForm
from maps.models import MapPointer
from locations.models import Location
from .models import Category, News
from .forms import NewsForm
# Use our mixin to allow only some users make actions
from places_core.mixins import LoginRequiredMixin
from places_core.permissions import is_moderator
from places_core.helpers import SimplePaginator, truncatehtml


class BasicNewsSerializer(object):
    """
    This is custom serializer for blog entries. It passes properly formatted.
    For more detailed info check BasicIdeaSerializer in ideas.views.
    """
    def __init__(self, obj):
        tags = []

        for tag in obj.tags.all():
            tags.append({
                'name': tag.name,
                'url': reverse('locations:tag_search',
                               kwargs={'slug':obj.location.slug,
                                       'tag':tag.name})
            })

        self.data = {
            'id'            : obj.pk,
            'title'         : obj.title,
            'slug'          : obj.slug,
            'link'          : obj.get_absolute_url(),
            'description'   : truncatehtml(obj.content, 240),
            'username'      : obj.creator.username,
            'user_full_name': obj.creator.get_full_name(),
            'creator_url'   : obj.creator.profile.get_absolute_url(),
            'user_id'       : obj.creator.pk,
            'avatar'        : obj.creator.profile.avatar.url,
            'date_created'  : timesince(obj.date_created),
            'edited'        : obj.edited,
            'comment_count' : obj.get_comment_count(),
            'tags'          : tags,
        }

        try:
            self.data['date_edited'] = timesince(obj.date_edited)
        except Exception:
            self.data['date_edited'] = ''

        if obj.category:
            self.data['category']     = obj.category.name
            self.data['category_url'] = reverse('locations:category_search',
                kwargs={
                    'slug'    : obj.location.slug,
                    'app'     : 'blog',
                    'model'   : 'news',
                    'category': obj.category.pk,
                })
        else:
            self.data['category'] = ''
            self.data['category_url'] = ''

    def as_array(self):
        return self.data


class BasicBlogView(View):
    """
    Basic view for our custom REST API, not involving Django rest framework.
    This API returns queryset in JSON format upon which backbone Blog collection
    is built.
    """
    def get_queryset(self, request, queryset):
        return queryset

    def get(self, request, slug=None, *args, **kwargs):
        if not slug:
            news_list = News.objects.all()
        else:
            location = Location.objects.get(slug=slug)
            news_list = News.objects.filter(location=location)

        news_list = self.get_queryset(request, news_list)
        ctx = {'results': []}

        for news in news_list:
            ctx['results'].append(BasicNewsSerializer(news).data)

        paginator = SimplePaginator(ctx['results'], 2)
        page = request.GET.get('page') if request.GET.get('page') else 1
        ctx['current_page'] = page
        ctx['total_pages'] = paginator.count()
        ctx['results'] = paginator.page(page)

        return HttpResponse(json.dumps(ctx))


class CategoryListView(ListView):
    """
    Categories for place's blog
    """
    model = Category
    context_object_name = 'categories'

    
class CategoryDetailView(DetailView):
    """
    Show category info
    """
    model = Category

    
class CategoryCreateView(LoginRequiredMixin, CreateView):
    """
    Create new category
    """
    model = Category
    fields = ['name', 'description']


class NewsListView(ListView):
    """
    News index for chosen location
    """
    model = News
    context_object_name = 'entries'

    
class NewsDetailView(DetailView):
    """
    Detailed news page
    """
    model = News

    def get_context_data(self, **kwargs):
        news = super(NewsDetailView, self).get_object()
        content_type = ContentType.objects.get_for_model(news)
        context = super(NewsDetailView, self).get_context_data(**kwargs)
        context['is_moderator'] = is_moderator(self.request.user, news.location)
        context['location'] = news.location
        context['content_type'] = content_type.pk
        context['title'] = news.title
        context['map_markers'] = MapPointer.objects.filter(
                content_type = ContentType.objects.get_for_model(self.object)
            ).filter(object_pk=self.object.pk)
        if self.request.user == self.object.creator:
            context['marker_form'] = AjaxPointerForm(initial={
                'content_type': ContentType.objects.get_for_model(self.object),
                'object_pk'   : self.object.pk,
            })
        return context

    
class NewsCreateView(LoginRequiredMixin, CreateView):
    """
    Create new entry
    """
    model = News
    form_class = NewsForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(NewsCreateView, self).form_valid(form)


class NewsUpdateView(LoginRequiredMixin, UpdateView):
    """
    Let owner edit his newses.
    """
    model = News
    form_class = NewsForm
    template_name = 'locations/location_news_form.html'

    def get_context_data(self, **kwargs):
        obj = super(NewsUpdateView, self).get_object()
        moderator = is_moderator(self.request.user, obj.location)
        if obj.creator != self.request.user and not moderator:
            raise PermissionDenied
        context = super(NewsUpdateView, self).get_context_data(**kwargs)
        context['is_moderator'] = moderator
        context['title'] = obj.title
        context['subtitle'] = _('Edit entry')
        context['location'] = obj.location
        return context
