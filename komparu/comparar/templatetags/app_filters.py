from django import template
register = template.Library()


# custom filters for accessing the results dictionary by winner and loser
@register.filter(name='get_winner_item')
def get_winner_item(dictionary, api):
    here = dictionary.get(api)
    sanitized = here['sanitized']
    return sanitized[here['winner']]

@register.filter(name='get_loser_item')
def get_loser_item(dictionary, api):
    here = dictionary.get(api)
    sanitized = here['sanitized']
    return sanitized[here['loser']]

@register.filter(name='get_win_percent')
def get_win_percent(dictionary):
    win_percent = dictionary['win_percent']
    return win_percent
