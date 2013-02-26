import datetime
from haystack import indexes
from cv.models import Person

class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', faceted=True)
    technology = indexes.MultiValueField(indexed=True, store=True)

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
