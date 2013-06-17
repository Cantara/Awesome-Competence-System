import datetime
from haystack import indexes
from cv.models.cvmodels import Person
from itertools import chain

def valid_XML_char_ordinal(i):
    return ( # conditions ordered by presumed frequency
        0x20 <= i <= 0xD7FF 
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
        )
    
class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', faceted=True)

    rendered = indexes.CharField(use_template=True, indexed=False)
    fulljson = indexes.CharField(use_template=True)
    
    technology = indexes.MultiValueField()

    last_edited = indexes.DateTimeField(model_attr='last_edited')

    location = indexes.CharField(model_attr='location', null=True, faceted=True)
    department = indexes.CharField(model_attr='department', null=True, faceted=True)
    years_of_experience = indexes.IntegerField(faceted=True)

    def get_model(self):
        return Person
    def index_queryset(self, using=None):
        return self.get_model().objects.all()
    def prepare_technology(self, obj):
        result = []
        for t in obj.technology_set.all():
            for tdata in t.data_as_list():
                result.append( tdata.encode('ascii', 'ignore') )
        return result
    def prepare_years_of_experience(self, obj):
        years = 0
        exp_and_work = list( chain( obj.experience_set.all(), obj.workplace_set.all() ) )
        for i in exp_and_work:
            if( i.from_year > 1969):
                yearspan = datetime.date.today().year - i.from_year
                if( years < yearspan and yearspan < 80):
                    years = yearspan
        return years

    def prepare(self, object):
        self.prepared_data = super(PersonIndex, self).prepare(object)
        self.prepared_data['text'] = ''.join( c for c in self.prepared_data['text'] if valid_XML_char_ordinal(ord(c)) )
        return self.prepared_data