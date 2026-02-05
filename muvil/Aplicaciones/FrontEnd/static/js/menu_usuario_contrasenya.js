function verificarPasswords() {

    // Ontenemos los valores de los campos de contraseñas
    pass1 = document.getElementById('nueva_password1');
    pass2 = document.getElementById('nueva_password2');

    // Verificamos si las constraseñas no coinciden
    if (pass1.value != pass2.value) {
        // Si las constraseñas no coinciden mostramos un mensaje
        document.getElementById("msg-error").classList.remove("d-none");

        return false;
    } else {
        // Si las contraseñas coinciden ocultamos el mensaje de error
        //document.getElementById("msg-error").classList.add("d-block");

        // Mostramos un mensaje mencionando que las Contraseñas coinciden
        //document.getElementById("msg-ok").classList.remove("d-none");

        // Desabilitamos el botón de login
        //document.getElementById("btn-guardar").disabled = true;

        // Refrescamos la página (Simulación de envío del formulario)
        //setTimeout(function() {
        //    location.reload();
        //}, 3000);

        return true;
    }

}