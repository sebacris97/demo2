from django.contrib import admin
from .models import Usuario, Perfil, Libro, Genero, Autor, Editorial, Novedad, Capitulo, Trailer
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from django_admin_listfilter_dropdown.filters import DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter


class NacimientoFilter(SimpleListFilter):
    
    title = 'Fecha de nacimiento'
    parameter_name = 'fecha_de_nacimiento'

    def lookups(self, request, model_admin):
        nacimientos = set([c.fecha_de_nacimiento for c in Usuario.objects.all()])
        return [(c, c) for c in nacimientos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(usuario__fecha_de_nacimiento=self.value())
        else:
            return queryset


class ProfileInline(admin.StackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Usuario'
    fk_name = 'user'

"""
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = True
    verbose_name_plural = 'Perfil'
    fk_name = 'usuario'
"""


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    UserAdmin.list_display += ('date_joined','get_nacimiento',)
    list_select_related = ('usuario', )
    list_filter = (('date_joined', DateRangeFilter),'date_joined',)+ UserAdmin.list_filter[0:3]

    def __init__(self, *args, **kwargs):
        super(UserAdmin,self).__init__(*args, **kwargs)
    
    def get_nacimiento(self, instance):
        return instance.usuario.fecha_de_nacimiento
    get_nacimiento.short_description = 'Fecha de nacimiento'
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)





# Register your models here.


# esto es una clase que pone el formulario de Capitulo en una linea
class CapituloInline(admin.TabularInline):
    model = Capitulo


# esto se llama decorator y ahorra el trabajo de registrar la clase y el libro
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):

    def get_genero(self, obj):
        return "\n".join([p.nombre for p in obj.genero.all()])

    get_genero.short_description = 'genero'  # Renames column head

    filter_horizontal = ('genero',)
    list_display = ('titulo', 'nropaginas', 'nrocapitulos', 'isbn', 'autor', 'editorial', 'get_genero', 'agnoedicion', 'contador', 'subido')
    search_fields = ('titulo', 'autor__nombre', 'autor__apellido', 'editorial__nombre', 'genero__nombre',)
    list_filter = (('subido', DateTimeRangeFilter),'subido',('agnoedicion', DateRangeFilter),('genero',RelatedDropdownFilter),)
    inlines = [CapituloInline]  # se registra en libro la clase creada anteriormente
    ordering = ('-subido','contador','titulo','-agnoedicion','isbn',)


@admin.register(Trailer)
class TrailerAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creacion',)
    search_fields = ('titulo', 'texto',)
    list_filter = (('creacion', DateTimeRangeFilter), 'creacion')


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido')
    search_fields = ('nombre', 'apellido')


@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Novedad)
class NovedadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creacion',)
    search_fields = ('titulo', 'texto',)
    list_filter = (('creacion', DateTimeRangeFilter), 'creacion')


admin.site.site_header = 'Sitio de administracion de Bookflix'
admin.site.index_title = 'Sitio de administracion de Bookflix'
admin.site.index_title = "Bienvenido al panel de administracion de Bookflix"
