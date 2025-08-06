# در فایل accounting/templatetags/accounting_tags.py

from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    A template tag to replace or add GET parameters to the current URL.
    It can handle multiple keyword arguments.
    e.g., {% url_replace request page=3 type='income' %}
    """
    query = context['request'].GET.copy()
    
    for key, value in kwargs.items():
        query[key] = value
        
    # رشته کوئری جدید را برمی‌گرداند
    return query.urlencode()