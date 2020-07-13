from django.core.management.base import BaseCommand
from bookflixapp.models import Perfil,  Usuario
from django.contrib.auth.models import User
from django.contrib.auth import hashers
            

class Command(BaseCommand):
    
    help = 'crea superusuario con email user@admin.com y password admin'

    def handle(self, *args, **kwargs):        
        
        email = 'user@admin.com'

        try:
            
            User.objects.get(email = email)
            self.stdout.write("el usuario con email: \"user@admin.com\"\ny password: \"admin\" ya existe")
            
        except User.DoesNotExist:
        
            pwd = hashers.make_password(password='admin')
            fn = 'user'
            ln = 'admin'
            tarjeta = '1234567891234567'
            fdn = '1997-08-15'
            
            user = User.objects.create( username     = email,
                                        email        = email,
                                        password     = pwd  ,
                                        first_name   = fn   ,
                                        last_name    = ln   ,
                                        is_superuser = True ,
                                        is_staff     = True ,
                                        is_active    = True ,)
            
            usuario = Usuario.objects.create( user                = user,
                                              tarjeta             = tarjeta,
                                              fecha_de_nacimiento = fdn    ,)
            
            Perfil.objects.create( usuario  = usuario ,
                                   username = fn      ,
                                   selected = True    ,)
