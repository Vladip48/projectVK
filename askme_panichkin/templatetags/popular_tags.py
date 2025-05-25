from django import template
from django.core.cache import cache

register = template.Library()

@register.inclusion_tag('includes/popular_tags.html')
def popular_tags():
    tags = cache.get('popular_tags', [])
    return {'tags': tags}

@register.inclusion_tag('includes/best_users.html')
def best_users():
    users = cache.get('best_users', [])
    return {'users': users}