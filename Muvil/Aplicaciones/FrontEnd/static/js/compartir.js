document.getElementById('shareButton').addEventListener('click', async () => {
    const url = document.getElementById('shareUrl').value;
    const fecha = document.getElementById('fecha').textContent;
    const hora = document.getElementById('hora').textContent;
    const desde = document.getElementById('desde').textContent;
    const hasta = document.getElementById('hasta').textContent;
    const precio = document.getElementById('precio').textContent;
    const plazas = document.getElementById('plazas').textContent;
    const equipaje = document.getElementById('equipaje').textContent;
    const title = 'Aquí tienes los detalles del viaje:';
    const text = 'Fecha: 22/10/2023\nHora:20:00\nOrigen: Murcia\nDestino: Albacete\nPrecio: 24€\nPlazas libres: 2';

    const full_text = ':chair\t ' + plazas + '\n' + ':clock\t ' + hora + '\n'
    const encodedfull_text = encodeURIComponent(url);
    const encodedUrl = encodeURIComponent(url);
    const shareData = {
      title: title,
      text: encodedfull_text,
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