from django import template 

register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def sudokuval(val):
    if val > 0 and val < 10:
        return str(val)
    else:
        return ""
    

