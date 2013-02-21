import datetime
from haystack import indexes
from cv.models import Person

class JobIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name', faceted=True)
 
    def get_model(self):
        return Person
 
    def index_queryset(self,using=None):
        return self.get_model().objects.all()
