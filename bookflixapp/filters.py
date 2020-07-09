import django_filters as df
from .models import Libro, Genero
from django import forms
from django.db import models

class LibroFilter(df.FilterSet):

    CHOICES = (
                ('ascendente','Mas leidos primero'),
                ('descendente','Menos leidos primero'),
                ('masnuevo','Mas nuevo primero'),
                ('masviejo','Mas viejo primero'),
              )

    ordering = df.ChoiceFilter(label='Ordering', choices=CHOICES, method='filter_by_order')
    
    class Meta:
        model = Libro
        fields = {
            'titulo': ['icontains'], 'autor': ['exact'], 'editorial': ['exact'], 'genero': ['exact'], 'agnoedicion': ['exact']
        ,'contador':['lt','gt']}
        filter_overrides = {
            models.ManyToManyField: {
                'filter_class': df.ModelMultipleChoiceFilter,
                'extra': lambda f: {
                    'widget': forms.SelectMultiple,
                    'queryset': Genero.objects.all()
                }
            }
        }

    def filter_by_order(self, queryset, name, value):
        
        if value == 'ascendente':
            expression = '-contador'
        elif value == 'descendente':
            expression = 'contador'
        elif value == 'masnuevo':
            expression = '-subido'
        else:
            expression = 'subido'
            
        return queryset.order_by(expression)

        
