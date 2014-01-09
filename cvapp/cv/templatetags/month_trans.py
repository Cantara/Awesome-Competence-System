from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def month_trans(month, lang):
	months = {
		'en': {
			'Jan':'Jan',
			'Feb':'Feb',
			'Mar':'Mar',
			'Apr':'Apr',
			'May':'May',
			'Jun':'Jun',
			'Jul':'Jul',
			'Aug':'Aug',
			'Sep':'Sep',
			'Oct':'Oct',
			'Nov':'Nov',
			'Dec':'Dec',
		},
		'no': {
			'Jan':'Jan',
			'Feb':'Feb',
			'Mar':'Mar',
			'Apr':'Apr',
			'May':'Mai',
			'Jun':'Jun',
			'Jul':'Jul',
			'Aug':'Aug',
			'Sep':'Sep',
			'Oct':'Okt',
			'Nov':'Nov',
			'Dec':'Des',
		},
		'se': {
			'Jan':'Jan',
			'Feb':'Feb',
			'Mar':'Mar',
			'Apr':'Apr',
			'May':'Maj',
			'Jun':'Jun',
			'Jul':'Jul',
			'Aug':'Aug',
			'Sep':'Sep',
			'Oct':'Okt',
			'Nov':'Nov',
			'Dec':'Dec',
		},
	}
	try:
		m = months[lang][month]
	except:
		m = month
	return m