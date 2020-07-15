from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, FileExtensionValidator, MinLengthValidator
from django.contrib.auth.models import User

# los validator te ahorran tener que hardcodear algunas validaciones que django ya provee


class Autor(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50, default='')

    def __str__(self):
        return '%s %s' % (self.nombre, self.apellido)

    class Meta:
        verbose_name_plural = "Autores"
        ordering = ["apellido", "nombre"]


class Genero(models.Model):
    nombre = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Generos"
        ordering = ["nombre"]


class Editorial(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Editoriales"
        ordering = ["nombre"]


class Capitulo(models.Model):
    libro = models.ForeignKey('Libro', on_delete=models.SET_NULL, null=True)  # libro al cual pertenece el capitulo
    numero = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Numero del capitulo',
                                         null=True, blank=True)
    nropaginas = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Numero de paginas",
                                             null=True, blank=True)

    def __str__(self):
        return str(self.libro) + ' - Capitulo: ' + str(self.numero)

    class Meta:
        verbose_name_plural = "Capitulos"
        ordering = ["numero"]
        unique_together = ('libro', 'numero',)  # no existen 2 capitulos 1 para el mismo libro

    def content_file_name(instance, filename):
        nombre = str(instance.numero) + '- ' + filename
        return '/'.join(['libros', instance.libro.titulo, nombre])

    pdf = models.FileField(upload_to=content_file_name,
                           validators=[FileExtensionValidator(['pdf'], 'Solo se permiten archivos pdf')])


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    nropaginas = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Numero de paginas")
    nrocapitulos = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Numero de capitulos")
    isbn = models.CharField(max_length=13, unique=True, validators=[
        RegexValidator('^(\d{10}|\d{13})$', 'El numero debe tener 10 o 13 digitos numericos')], verbose_name="ISBN")
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)
    editorial = models.ForeignKey(Editorial, on_delete=models.CASCADE)
    genero = models.ManyToManyField(Genero)
    agnoedicion = models.DateField(verbose_name="Año de edicion")

    trailer = models.ForeignKey('Trailer', on_delete=models.CASCADE)

    contador = models.PositiveIntegerField(default=0, editable=False, verbose_name='Veces leido')

    subido = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de carga")

    def get_trailer(self):
        return self.trailer.get_texto()

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Libros"
        ordering = ["-subido", "-contador", "titulo", "-agnoedicion", "isbn"]

    def get_imagen(self):
        return self.trailer.get_imagen()


class Novedad(models.Model):
    titulo = models.CharField(max_length=100)
    texto = models.TextField()
    creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creacion")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name_plural = "Novedades"

        ordering = ["-creacion"]


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='')
    tarjeta = models.CharField(max_length=16, validators=[
        RegexValidator('^(\d{16})$',
                       'Debe introducir un numero de 16 digitos')], verbose_name="Tarjeta de credito")
    fecha_de_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    cantPerfiles = models.IntegerField(default=2)
    is_premium = models.BooleanField(default=False)

    class Meta:
        ordering = ["user__email", "fecha_de_nacimiento"]
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.user.email


class Trailer(models.Model):

    def content_file_name(instance, filename):
        nombre = filename
        return '/'.join(['trailers', instance.titulo, nombre])

    titulo = models.CharField(max_length=200, default='NONE', verbose_name="Titulo")
    imagen = models.ImageField(null=True, upload_to=content_file_name, default='default.jpg', verbose_name="Imagen")
    texto = models.TextField(max_length=1000, default='NONE', verbose_name="Texto")
    creacion = models.DateTimeField(auto_now_add=True, verbose_name="Creacion")

    def __str__(self):
        return self.titulo + ' trailer'

    class Meta:
        verbose_name_plural = "Trailers"
        ordering = ["-creacion"]

    def get_texto(self):
        return self.texto

    def get_imagen(self):
        return self.imagen.url


class Perfil(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=20, verbose_name='Nombre de usuario')
    historial = models.ManyToManyField('Libro', verbose_name='Historial', related_name="historial")
    favoritos = models.ManyToManyField('Libro', verbose_name='Favoritos', related_name="favoritos")
    selected = models.BooleanField(default=True, verbose_name='Perfil seleccionado')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = "Perfiles"


class Comentario(models.Model):
    perfil = models.ForeignKey('Perfil', on_delete=models.SET_NULL, null=True)
    libro = models.ForeignKey('Libro', on_delete=models.SET_NULL, null=True)
    texto = models.TextField(max_length=1000, validators=[MinLengthValidator(20)])
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        """
        los datetimefield son datetime.datetime objects de python
        en la base de datos es almacena la fecha en utc y cuando uno cambia en settings
        la time_zone solo cambia a fines de traduccion de django pero no el como se almacena en la db
        por eso es necesaria transformarla cuando se muestra como string el objeto directo desde la db
        y para eso usamos el metodo astimezone de datime que devuelve el objeto datetime de la timezone local
        """
        perfil = str(self.perfil)
        fecha  = str(self.fecha.astimezone().strftime("%d-%m-%Y"))
        hora   = str(self.fecha.astimezone().strftime("%H:%M"))
        return 'Comentado por ' + perfil + ' el ' + fecha + ' a las ' + hora

