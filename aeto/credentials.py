from decouple import config

def modoDB(modo=config('MODO')):
    # Base de Pruebas
    if modo == 'local':
        return{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aeto',
        'USER': 'postgres',
        'PASSWORD': config('PASSWORD'),
        'HOST': 'localhost',
        'PORT': config('PORT'),
    }
        
    #Base de despliege aetoweb (No tocar)
    if modo == 'despliegue':
        return{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aeto',
        'USER': 'super',
        'PASSWORD': 'iGkG1B#@j',
        'HOST': 'carlossantoyo-2681.postgres.pythonanywhere-services.com',
        'PORT': '12681',
    }

    #Base de despliegue local (No tocar)
    if modo == 'despliegue_local':
        return{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'aeto',
        'USER': 'super',
        'PASSWORD': 'iGkG1B#@j',
        'HOST': '127.0.0.1',
        'PORT': '1025',
    }

    if modo == 'digitalocean':
        return{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'defaultdb',
        'USER': 'doadmin',
        'PASSWORD': 'AVNS_DLiNO-kKhTvSv-I',
        'HOST': 'galgowebservices-do-user-11664977-0.b.db.ondigitalocean.com',
        'PORT': '25060',
    }
        