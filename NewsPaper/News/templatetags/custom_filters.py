from re import sub
from django import template


register = template.Library()


@register.filter(name='censor')
def censor(value, arg):
    text_no_censor = str(value)
    words = ['блин', 'гад', 'лох']

    for word in words:
        text_no_censor = sub(word, str(arg), text_no_censor)

    return text_no_censor


@register.simple_tag
def url_qs_filter(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)

    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)

    return url

