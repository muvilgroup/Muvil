const notificacionSwal = (title,text,icon,confirmButtonText) => {
    Swal.fire({
        titleText: title,
        text: text,
        icon: icon, // valores posibles: warning, error, info, success
        confirmButtonText: confirmButtonText
    });
};