genero = (
    ('F', 'Femenino'),
    ('M', 'Masculino')
)

documentos_identidad = (
    ('DNI', 'DNI'),
    ('NIE', 'NIE'),
    ('PASAPORTE', 'PASAPORTE')
)

tipo_vehiculo = (
    ('C', 'Combustible'),
    ('E', 'Electrico'),
    ('H', 'Hibrido')
)

equipaje = (
    ('EP', 'Maleta pequeña'),
    ('EM', 'Maleta mediana'),
    ('EG', 'Maleta grande')
)

prestigio = (
    ('B', 'Bronce'),
    ('P', 'Plata'),
    ('Pl', 'Platino'),
    ('O', 'Oro'),
    ('D', 'Diamante')
)

categorias_puntuacion = (
    (1, 'Muy Mal'),
    (2, 'Mal'),
    (3, 'Bien'),
    (4, 'Muy Bien'),
    (5, 'Excelente')
)

estado_transferencia = (
    (1, 'Pendiente'),
    (2, 'Realizado'),
    (3, 'Reembolso'),
    (4, 'Denegado'),
    (5, 'Error')
)

tipo_transferencia = (
    ('C', 'Cobro'),
    ('P', 'Pago')
)

tipo_descuento = (
    ('OP', 'Opinion Publicada'),
    ('O', 'Otros')
)

estados_viajes = (
    (1, 'Pendiente'),
    (2, 'Finalizado'), # Viaje terminado con éxito tras la aprobación de los pasajeros o tras 24 horas de la no notificacion de problemas
    (3, 'Cancelado'),
    (4, 'Realizado'), # Viaje que se acaba de realizar en teoria, momento en el que los pasajeros pueden indicar si han habido incidencias en el viaje
    (5, 'Problemático')
)

# Estado relativo a la reserva de la plaza
estados_plazas = (
    (1, 'Pendiente'),
    (2, 'Confirmado'),
    (3, 'Rechazado'),
    (4, 'Cancelado'),
)

# Estado relativo a la conclusión del viaje de la plaza
estados_plazas_viaje = (
    (1, 'Sin Estado'),
    (2, 'Realizado'),
    (3, 'Finalizado'),
    (4, 'Problemático')
)

modelos = (
    ('Localizaciones', 'Localizaciones'),
    ('<Pendiente añadir>', '<Pendiente añadir>')
)

estados_pref_mascotas = (
    (1, 'Sin mascotas'),
    (3, 'Adoro las mascotas'),
)

estados_pref_fumar = (
    (1, 'No fumar'),
    (3, 'Permitido'),
)

estados_pref_comida = (
    (1, 'Sin comida'),
    (3, 'Comida incluida'),
)

estados_pref_musica = (
    (1, 'Sin música'),
    (3, 'Con música'),
)
