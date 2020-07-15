from django.shortcuts import render, redirect
from bookflixapp.models import Trailer, Libro, Novedad, Capitulo, Perfil, Usuario, Comentario
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth import hashers, authenticate
from django.contrib.auth import login as do_login
from .forms import RegistrationForm, CreateProfileForm, ComentarioForm
from .forms import CustomAuthenticationForm as AuthenticationForm
from .filters import LibroFilter

from django.contrib.auth.decorators import login_required
from django.db.models import F


# Create your views here.


def perfil_actual(request):
    usuario=Usuario.objects.filter(user__email=str(request.user))  #me quedo con el usuario logueado
    perfil=Perfil.objects.filter(usuario__user__email=str(usuario[0]), selected=True) #me quedo con el perfil seleccionado
    return perfil[0]


def agregar_favoritos(id_libro,perfil):
    libro = Libro.objects.filter(id=id_libro)
    perfil.favoritos.add(*libro)

def eliminar_favoritos(id_libro,perfil):
    libro = Libro.objects.filter(id=id_libro)
    perfil.favoritos.remove(*libro)


@login_required
def ver_libros(request,choice=''):
    perfil = perfil_actual(request)
    favoritos = list(perfil.favoritos.values_list('id', flat=True))
    if request.method == 'POST':
        id_libro = int(  list(request.POST.keys())[1]  )
        #request.POST es un diccionario (dict_object) que en [0] tiene el csrf_token
        #y en 1 el string del ID del libro que clickie (por eso hago el casteo a int)
        if id_libro not in favoritos:
            agregar_favoritos(id_libro,perfil)
        else:
            eliminar_favoritos(id_libro,perfil)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        #para redirigir a la misma url donde estaba

    #favoritos, historial y ver libros son lo mismo, solo cambia el
    #queryset que se muestra (por eso directamente resumi todo en un
    #parametro que determina el queryset elegido)

    if choice == 'favoritos':
        qs = perfil.favoritos
    elif choice == 'historial':
        qs = perfil.historial
    else:
        qs = Libro.objects.all()

    filtro = LibroFilter(request.GET, queryset=qs)

    return render(request, "ver_libros.html", {"filter": filtro,
                                               "favoritos": favoritos})


def action(request, pk_libro, pk_capitulo):
    libro = Libro.objects.filter(id=pk_libro)
    libro.update(contador=F('contador') + 1)
    capitulo = Capitulo.objects.filter(id=pk_capitulo)[0]
    perfil = perfil_actual(request)
    perfil.historial.add(*libro) #lo agrgo a la lista de libros leidos
    return redirect(capitulo.pdf.url)


def do_comment(request, form, libro):
    if form.is_valid():
        texto = form.cleaned_data["texto"]
        Comentario.objects.create(perfil=perfil_actual(request), texto=texto, libro=libro)


def borrarComentario(request, comentariopk, libropk):
    comentario_actual = Comentario.objects.get(id=comentariopk)
    if request.method == "POST":
        if perfil_actual(request).id == comentario_actual.perfil.id:
            comentario_actual.delete()
        return HttpResponseRedirect('/verCapitulos/'+str(libropk))
    return render(request, "borrar_comentario.html", {'libro_id':libropk})

@login_required
def ver_capitulos(request, pk):
    capitulos = Capitulo.objects.filter(libro__id=pk)
    if len(capitulos) > 0:  # parche temporal para los libros que no tienen capitulos
        libro = capitulos[0].libro
        perfilactual = perfil_actual(request)
        comentarios = Comentario.objects.filter(libro__id=pk)
        comentario_form = ComentarioForm(request.POST or None)
        if request.method == 'POST':
            if request.POST.get('enviar'):
                do_comment(request, comentario_form, libro)
            if request.POST.get('eliminar'):
                borrarComentario(request, comentario_form, libro)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # el parametro lo recibe de urls. lo que hago es filtrar los capitulos
        # que pertenecen al libro que recibo como parametro
        # (si hiciese objects.all() me estoy quedando con todos los capitulos de todos los libros)

        return render(request, "ver_capitulos.html", {"capitulos": capitulos,
                                "libro": libro, "comentarios": comentarios,
                                "comentario_form": comentario_form, "perfil_actual": perfilactual})
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


def login(request):
    # Creamos el formulario de autenticación
    form = AuthenticationForm(data=request.POST or None)
    if request.method == "POST":
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)
            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)

                # Si el usuario es administrador
                if request.user.is_superuser:
                    # Lo redireccionamos a la pagina del admin
                    return redirect('/admin')
                else:
                    # Y sino le redireccionamos a la portada
                    return redirect('/')
    # Si llegamos al final renderizamos el formulario
    return render(request, "registration/login.html", {'form': form})



@login_required
def createprofile(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    pp = Perfil.objects.filter(usuario=usuario)
    c = pp.count()
    if request.method == "POST":
        form = CreateProfileForm(user=user, data=request.POST)
        if form.is_valid():
            profilename = form.cleaned_data["profilename"]
            p = Perfil.objects.filter(usuario=usuario, selected=True)
            per = p[0]
            per.selected = False
            per.save()
            profile = Perfil(usuario=usuario, username=profilename)
            profile.save()
            if profile is not None:
                return HttpResponseRedirect("/")
        else:
            return render(request, "crear_perfil.html", {'form': None})
    else:
        form = CreateProfileForm(user)
        return render(request, "crear_perfil.html", {'form': form, 'cant1': usuario.cantPerfiles, 'cant2': c})


@login_required
def verperfil(request):
    perfil = perfil_actual(request)
    return render(request, 'perfil.html', {"perfil": perfil})


@login_required
def selecperfil(request):

    #me quedo con el usuario logueado
    usuario = Usuario.objects.get(user=request.user)
    #me quedo con los perfiles del usuario logueado
    perfiles = Perfil.objects.filter(usuario=usuario)

    #me quedo con el perfil actual
    p_actual = perfil_actual(request)

    #si se prsiona seleccionar
    if request.method == "POST":

        #me quedo con el id del usuario que seleccione
        p_seleccionado_n = request.POST['nombre']
        #me quedo con el objeto del usuario que seleccione
        p_seleccionado = Perfil.objects.get(username=p_seleccionado_n)

        #si el perfil que seleccione no es el que actualmente esta seleccinado
        if p_seleccionado.selected == False:

            #"deselecciono" el perfil actual
            p_actual.selected = False
            #y actualizo la base de datos
            p_actual.save(update_fields=['selected'])
            #ahora marco el que seleccione como seleccionado
            p_seleccionado.selected = True
            #y acutalizo la base de datos
            p_seleccionado.save(update_fields=['selected'])

        #redireccionamos a verperfil
        return HttpResponseRedirect('/perfil')

    #renderizo el template con los perfiles del usuario logueado
    return render(request, 'selec_perfil.html', {"perfiles": perfiles,"p_actual":p_actual})


@login_required
def verusuario(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')
    else:
        user = request.user
        usuario = Usuario.objects.get(user=user)
        return render(request, 'ver_usuario.html', {'user': user, 'usuario': usuario})


@login_required
def borrarperfil(request):
    usuario = Usuario.objects.get(user=request.user)
    perfiles = Perfil.objects.filter(usuario=usuario)
    cant = perfiles.count()
    if request.method == "POST":
        p_seleccionado_id = request.POST['nombre']
        p_seleccionado = Perfil.objects.get(username=p_seleccionado_id)
        p = Perfil.objects.filter(usuario=usuario)
        sel = p_seleccionado.selected
        for per in p:
            if per != p_seleccionado:
                if sel:
                    per.selected = True
                    per.save()
                p_seleccionado.delete()
                break
        return render(request, 'borrar_perfil.html', {"cant": -1})
    return render(request, 'borrar_perfil.html', {"perfiles": perfiles, "cant": cant})


@login_required
def modificarperfil(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    perfil = perfil_actual(request)
    cant = 1
    if request.method == 'POST':
        nuevo_per = request.POST['nuevo']
        per = Perfil.objects.filter(usuario=usuario)
        for p in per:
            if p.username == nuevo_per:
                cant = -1
                return render(request, 'modificar_perfil.html', {'perfil': perfil, 'cant': cant })
        perfil.username = nuevo_per
        perfil.save()
        return HttpResponseRedirect('/perfil')
    return render(request, 'modificar_perfil.html', {'perfil': perfil, 'cant': cant })


@login_required
def modificardatos(request):
    user = request.user
    usuario = Usuario.objects.get(user=user)
    if request.method == 'POST':
        nom = request.POST['nombre']
        ape = request.POST['apellido']
        contra = request.POST['contraseña']
        fecha = request.POST['fecha']
        if nom != "":
            user.first_name = nom
        if ape != "":
            user.last_name = ape
        if contra != "":
            realpass = hashers.make_password(contra)
            user.password = realpass
        if fecha != "":
            usuario.fecha_de_nacimiento = fecha
        user.save()
        usuario.save()
        return HttpResponseRedirect('/')
    else:
        return render(request, 'modf_usuario.html', {'user': user, 'usuario': usuario})

@login_required
def borrarusuario(request):
    user = request.user
    form = AuthenticationForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            usr = authenticate(username=username, password=password)
            if usr is not None and usr.email == user.email:
                usr.delete()
                return HttpResponseRedirect("/")
    return render(request, 'borrar_usuario.html', {'form': form, 'user': user})
