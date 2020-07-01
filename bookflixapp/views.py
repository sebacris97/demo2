from django.shortcuts import render, redirect
from bookflixapp.models import Trailer, Libro, Novedad, Capitulo, Perfil, Usuario
from datetime import timedelta
from django.utils import timezone
from django.http import request as rq

from django.contrib.auth import logout as do_logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import hashers
from django.contrib.auth import login as do_login
from .forms import RegistrationForm, LoginForm, CreateProfileForm
from .filters import LibroFilter

from django.contrib.auth.decorators import login_required


# Create your views here.


def perfil_actual(request):
    usuario=Usuario.objects.filter(user__email=str(request.user))  #me quedo con el usuario logueado
    perfil=Perfil.objects.filter(usuario__user__email=str(usuario[0]), selected=True) #me quedo con el perfil seleccionado
    return perfil[0]

@login_required
def ver_historial(request):
    perfil = perfil_actual(request)
    historial = perfil.historial.all()
    return render(request, "ver_historial.html", {'historial':historial})    

@login_required
def ver_libros(request):
    filtro = LibroFilter(request.GET, queryset=Libro.objects.all())
    print(filtro)
    return render(request, "ver_libros.html", {"filter": filtro})

@login_required
def ver_capitulos(request, pk):
    capitulos = Capitulo.objects.filter(libro__id=pk)
    if len(capitulos) > 0:  # parche temporal para los libros que no tienen capitulos
        titulo = capitulos[0].libro
        
        perfil = perfil_actual(request)
        libro = Libro.objects.filter(id=pk) #me quedo con el libro clickeado
        perfil.historial.add(*libro) #lo agrgo a la lista de libros leidos

        # el parametro lo recibe de urls. lo que hago es filtrar los capitulos
        # que pertenecen al libro que recibo como parametro
        # (si hiciese objects.all() me estoy quedando con todos los capitulos de todos los libros)

        return render(request, "ver_capitulos.html", {"capitulos": capitulos, "titulo": titulo})
    else:
        return redirect('/')  # si no se le subio capitulo te manda a index


@login_required
def post_search(request):
    
    return redirect('/verLibros/?titulo__icontains=' + request.POST['search'])

def index(request):
    d = timezone.now() - timedelta(days=7)
    trailers = Trailer.objects.filter(creacion__gte=d)
    novedades = Novedad.objects.filter(creacion__gte=d)
    if request.user.is_authenticated:
        if request.user.is_superuser:
            nombre_perfil = 'admin'
        else:
            perfil = perfil_actual(request)
            nombre_perfil = str(perfil)
        return render(request, "index.html", {"trailers":trailers,"novedades": novedades,"nombre_perfil":nombre_perfil})
    return render(request, "index.html", {"trailers":trailers,"novedades": novedades})

def register(request):
    # Creamos el formulario de autenticación vacío
    form = RegistrationForm(data=request.POST or None)
    if request.method == "POST":
        
        # Si el formulario es válido...
        if form.is_valid():

            # Creamos la nueva cuenta de usuario
            username = form.cleaned_data["email"]
            realpassword = hashers.make_password(password=form.cleaned_data["password1"])
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            tarjeta = form.cleaned_data["tarjeta"]
            fecha = form.cleaned_data["fecha_de_nacimiento"]
            u = User(username=username, first_name=first_name, last_name=last_name, password=realpassword, email=username)
            u.save()
            user = Usuario(user=u, fecha_de_nacimiento=fecha, tarjeta=tarjeta)
            # Si el usuario se crea correctamente 
            if user is not None:
                # Hacemos el login manualmente
                user.save()
                p = Perfil(usuario=user, username=u.first_name)
                p.save()
                do_login(request, u)
                # Y le redireccionamos a la portada
                return redirect('/')


    # Si llegamos al final renderizamos el formulario
    return render(request, "registration/register.html", {'form': form})


def login_view(request):
    # Creamos el formulario de autenticación vacío
    if request.method == "POST":
        # Recuperamos las credenciales validadas
        username = request.POST["email"]
        password = request.POST["pass"]
        # Verificamos las credenciales del usuario
        user = authenticate(username=username, password=password)
        # Si existe un usuario con ese nombre y contraseña
        if user is not None:
            # Hacemos el login manualmente
            do_login(request, user)
            if user.is_superuser:
                return redirect("/admin")  # or your url name
                # Y le redireccionamos a la portada
            else:
                return redirect("/")
    # Si llegamos al final renderizamos el formulario
    return render(request, "registration/login.html")


def logout(request):
    # Finalizamos la sesión
    do_logout(request)
    # Redireccionamos a la portada
    return redirect('/')


@login_required
def createprofile(request):
    if request.method == "POST":
        form = CreateProfileForm(data=request.POST)
        if form.is_valid():
            profilename = form.cleaned_data["profilename"]
            user = request.user
            usuario = Usuario.objects.get(user=user)
            p = Perfil.objects.filter(usuario=usuario, selected=True)
            per = p[0]
            per.selected = False
            per.save()
            profile = Perfil(usuario=usuario, username=profilename)
            profile.save()
            if profile is not None:
                return redirect("/")
    else:
        form = CreateProfileForm()
        return render(request, "crear_perfil.html", {'form': form})


@login_required
def verperfil(request):
    perfil = str(perfil_actual(request))
    return render(request, 'perfil.html', {"perfil": perfil})


@login_required
def selecperfil(request):
    if request.method == "GET":
        user = request.user
        usuario = Usuario.objects.filter(user=user)
        perfiles = Perfil.objects.filter(usuario=usuario[0])
        return render(request, 'selec_perfil.html', {"perfiles": perfiles})
    if request.method == "POST":
        return render(request, 'perfil.html')
