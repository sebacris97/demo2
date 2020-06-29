# Generated by Django 3.0.7 on 2020-06-29 08:44

import bookflixapp.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Autor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(default='', max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Autores',
                'ordering': ['apellido', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Editorial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name_plural': 'Editoriales',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=25, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Generos',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Libro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('nropaginas', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Numero de paginas')),
                ('nrocapitulos', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Numero de capitulos')),
                ('isbn', models.CharField(max_length=13, unique=True, validators=[django.core.validators.RegexValidator('^(\\d{10}|\\d{13})$', 'El numero debe tener 10 o 13 digitos numericos')], verbose_name='ISBN')),
                ('agnoedicion', models.DateField(verbose_name='Año de edicion')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookflixapp.Autor')),
                ('editorial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookflixapp.Editorial')),
                ('genero', models.ManyToManyField(to='bookflixapp.Genero')),
            ],
            options={
                'verbose_name_plural': 'Libros',
                'ordering': ['titulo'],
            },
        ),
        migrations.CreateModel(
            name='Novedad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('texto', models.TextField()),
                ('creacion', models.DateTimeField(auto_now_add=True, verbose_name='Creacion')),
            ],
            options={
                'verbose_name_plural': 'Novedades',
                'ordering': ['-creacion'],
            },
        ),
        migrations.CreateModel(
            name='Trailer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(default='NONE', max_length=200, verbose_name='Titulo')),
                ('imagen', models.ImageField(default='default.jpg', null=True, upload_to=bookflixapp.models.Trailer.content_file_name, verbose_name='Imagen')),
                ('texto', models.TextField(default='NONE', max_length=500, verbose_name='Texto')),
                ('creacion', models.DateTimeField(auto_now_add=True, verbose_name='Creacion')),
            ],
            options={
                'verbose_name_plural': 'Trailers',
                'ordering': ['-creacion'],
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarjeta', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator('^(\\d{16})$', 'Debe introducir un numero de 16 digitos')], verbose_name='Tarjeta de credito')),
                ('fecha_de_nacimiento', models.DateField()),
                ('user', models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('selected', models.BooleanField(default=True)),
                ('historial', models.ManyToManyField(to='bookflixapp.Libro')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bookflixapp.Usuario')),
            ],
            options={
                'verbose_name_plural': 'Perfiles',
            },
        ),
        migrations.AddField(
            model_name='libro',
            name='trailer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookflixapp.Trailer'),
        ),
        migrations.CreateModel(
            name='Capitulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Numero del capitulo')),
                ('nropaginas', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Numero de paginas')),
                ('pdf', models.FileField(upload_to=bookflixapp.models.Capitulo.content_file_name, validators=[django.core.validators.FileExtensionValidator(['pdf'], 'Solo se permiten archivos pdf')])),
                ('libro', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bookflixapp.Libro')),
            ],
            options={
                'verbose_name_plural': 'Capitulos',
                'ordering': ['numero'],
                'unique_together': {('libro', 'numero')},
            },
        ),
    ]
