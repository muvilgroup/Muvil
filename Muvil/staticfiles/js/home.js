const $numAlert = document.getElementById('numAlert');

(function () {
    if($numAlert.value == 1){
        //notificacionSwal("ERROR!", "No existe ningún usuario con ese Email/Contraseña", "error", "Mil Perdones!");
        //alert("No existe ningún usuario con ese Email/Contraseña");
        Swal.fire({
            titleText: "ERROR!",
            text: "No existe ningún usuario con ese Email/Contraseña",
            icon: "error", // valores posibles: warning, error, info, success
            confirmButtonText: "Mil Perdones!"
        });
    }

    if($numAlert.value == 2){
        Swal.fire({
            titleText: "Que bien verte por aquí!!!",
            text: "Busca tu próxima aventura de viaje!!!",
            icon: "success", // valores posibles: warning, error, info, success
            confirmButtonText: "Vamos a ello!!!"
        });
    }

    if($numAlert.value == 3){
        Swal.fire({
            titleText: "Gracias por unirte a la familia!!!",
            text: "Tu usuario se ha creado correctamente. \n Busca tu primera aventura de viaje!!!",
            icon: "success", // valores posibles: warning, error, info, success
            confirmButtonText: "OK!!!"
        });
    }

    if($numAlert.value == 4){
        Swal.fire({
            titleText: "Bien Hecho!!!",
            text: "Tu viaje ha sido publicado con éxito!!!",
            icon: "success", // valores posibles: warning, error, info, success
            confirmButtonText: "OK!!!"
        });
    }

})();


