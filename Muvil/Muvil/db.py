POSTGRE_LOCAL = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'Muvil',
        'USER':'postgres',
        'PASSWORD':'SuperUsuario2022.',
        'HOST':'127.0.0.1',  # localhost también valdría
        'DATABASE_PORT':'5432'
    }
}

POSTGRE_MUVIL = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'muvil_db',
        'USER': 'admin_db',
        'PASSWORD': 'Cavives8',
        'HOST': 'localhost',
        'DATABASE_PORT': '5432'
    }
}

SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'Muvil.sqlite3',
    }
}