document.getElementById('shareButton').addEventListener('click', async () => {
    const url = document.getElementById('shareUrl').value;
    const title = 'Aquí tienes los detalles del viaje:';
    const text = 'Fecha: 22/10/2023\nHora:20:00\nOrigen: Murcia\nDestino: Albacete\nPrecio: 24€\nPlazas libres: 2';
    const encodedUrl = encodeURIComponent(url);
    const shareData = {
      title: title,
      text: text,
      url: url,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // Mostrar enlaces de fallback si la API Web Share no está disponible
        document.getElementById('fallbackShare').style.display = 'block';
      }
    } catch (err) {
      console.error('Error al compartir:', err);
    }
  });