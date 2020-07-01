
  first_name = document.getElementById("id_first_name");
  first_name.setAttribute("class","form-control");
  first_name.setAttribute("placeholder","Ingrese su nombre");

  last_name = document.getElementById("id_last_name");
  last_name.setAttribute("class","form-control");
  last_name.setAttribute("placeholder","Ingrese su apellido");

  email = document.getElementById("id_email");
  email.setAttribute("class","form-control");
  email.setAttribute("placeholder","Ingrese su email");

  password1 = document.getElementById("id_password1");
  password1.setAttribute("class","form-control");
  password1.setAttribute("placeholder","Ingrese su contraseña");

  password2 = document.getElementById("id_password2");
  password2.setAttribute("class","form-control");
  password2.setAttribute("placeholder","Ingrese nuevamente su contraseña");

  fecha_de_nacimiento = document.getElementById("id_fecha_de_nacimiento");
  fecha_de_nacimiento.setAttribute("type","date");
  fecha_de_nacimiento.setAttribute("max","9999-12-31");
  fecha_de_nacimiento.setAttribute("class","form-control");

  tarjeta = document.getElementById("id_tarjeta");
  tarjeta.setAttribute("type","text");
  tarjeta.setAttribute("class","form-control");
  tarjeta.setAttribute("placeholder","Ingrese el numero de su tarjeta de credito");