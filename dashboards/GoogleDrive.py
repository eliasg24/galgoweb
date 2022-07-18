from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import FileNotUploadedError
import webbrowser

from aeto.settings import BASE_DIR

directorio_credenciales = str(BASE_DIR) + '/credentials_module.json'

# INICIAR SESION
def login():
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = directorio_credenciales
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credenciales)
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth(port_numbers=[8092])
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
        
    gauth.SaveCredentialsFile(directorio_credenciales)
    credenciales = GoogleDrive(gauth)
    return credenciales

def crear_archivo_texto(nombre_archivo,contenido,id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'title': nombre_archivo,\
                                       'parents': [{"kind": "drive#fileLink",\
                                                    "id": id_folder}]})
    archivo.SetContentString('Hey !')
    archivo.Upload()
    return archivo['id']

# SUBIR UN ARCHIVO A DRIVE
def subir_archivo(ruta_archivo,id_folder, nombre):
    """Funcion que sube archivos (Solo uno) a Google Drive

    Args:
        ruta_archivo (str): Cadena que guarda la ubicación del archivo
        id_folder (str): Cadena del folder donde se va a guardar el archivo
        nombre (str): Nombre del archivo que se subira

    Returns:
        str: Id del archivo en Drive
    """
    credenciales = login()
    archivo = credenciales.CreateFile({'parents': [{"kind": "drive#fileLink",\
                                                    "id": id_folder}]})
    archivo['title'] = nombre
    archivo.SetContentFile(ruta_archivo)
    archivo.Upload()
    return archivo['id']

def crear_carpeta(nombre_carpeta,id_folder):
    """Funcion que crea carpetas en google drive

    Args:
        nombre_carpeta (str): Nombre de la carpeta que se subira a Google Drive
        id_folder (str): Cadena del folder donde se va a guardar el archivo

    Returns:
        str: Id del archivo en Drive
    """
    credenciales = login()
    folder = credenciales.CreateFile({'title': nombre_carpeta, 
                               'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [{"kind": "drive#fileLink",\
                                                    "id": id_folder}]})
    folder.Upload()
    return folder['id']
    
def borrar_recuperar(id_archivo):
    """Funcion que borra carpetas del drie (Las envia a la papelera de reciclaje)

    Args:
        id_folder (str): Cadena del folder donde se va a guardar el archivo
    """
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_archivo})
    # MOVER A BASURERO
    archivo.Trash()
    # SACAR DE BASURERO
    #archivo.UnTrash()
    # ELIMINAR PERMANENTEMENTE
    #archivo.Delete()
    
    
# BUSCAR ARCHIVOS
def busca(query):
    resultado = []
    credenciales = login()
    # Archivos con el nombre 'prueba': title = 'prueba'
    # Archivos que contengan 'prueba' y 'pruebars': title contains 'prueba' and title contains 'pruebars'
    # Archivos que NO contengan 'prueba': not title contains 'prueba'
    # Archivos que contengan 'prueba' dentro del archivo: fullText contains 'prueba'
    # Archivos en el basurero: trashed=true
    # Archivos que se llamen 'prueba' y no esten en el basurero: title = 'prueba' and trashed = false
    lista_archivos = credenciales.ListFile({'q': query}).GetList()
    for f in lista_archivos:
        # ID Drive
        print('ID Drive:',f['id'])
        print('Tipo de archivo:',f['mimeType'])
        # Link de visualizacion embebido
        # Link de descarga
        if str(f['mimeType']) != 'application/vnd.google-apps.folder':
            resultado.append(f['id'])
    
    return resultado

def cambiar_nombre(id_folder, new_name):
    """Funcion que cambia el nombre de un archivo

    Args:
        id_folder (str): Cadena del folder donde se va a guardar el archivo
        new_name (str): Cadena con el nuevo nombre del archivo
    """
    credenciales = login()
    update_file = credenciales.CreateFile({'id': id_folder})
    update_file['title'] #<- Esto quiero quitarlo xd
    update_file['title'] = str(new_name)
    update_file.Upload()
    print('Finish')
    
    
ID_FOLDER = '1kEOreah3tuxntZwAUGc5Wzgu-LqFWKoE'
    
if __name__ == "__main__":
    #nombre = "Hola2"
    #ruta_archivo = r"C:\Users\josec\Downloads\CA.pdf"
    #id_folder = '1ZGmYEiiOIuoPK773_TiK-8ifxoI_TO_v'
    #a = crear_archivo_texto('Hectorputo.txt','Hey MoonCoders',id_folder)
    #a = subir_archivo(ruta_archivo,id_folder, nombre)
    #link = f'https://drive.google.com/file/d/{a}/view'
    #webbrowser.open(f'{link}')  # Go to example.com
    #cambiar_nombre('1Or9T6J3nHIP-ZdckIAQTCgRWDDly9Ypc', 'hola')
    #print(busca("title = ''nnnn"))
    ruta = r"C:\Users\josec\Downloads\meme.jpg"
    subir_archivo(ruta, ID_FOLDER, 'meme')
    pass