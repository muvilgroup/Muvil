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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgresdb_lf3j',
        'USER': 'postgresdb_lf3j_user',
        'PASSWORD': '7b6M5O8fxumGpo6qvvVc8sennoRHzhhT',
        'HOST': 'dpg-d5vvi83uibrs73d3uc7g-a.oregon-postgres.render.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}


SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'Muvil.sqlite3',
    }
}