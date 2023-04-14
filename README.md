# Instalacion

### Crea el entorno virtual

virtualenv env

### Activa el entorno virtual

source env/bin/activate

### Instala los paquetes necesarios

pip install -r requirements.txt

# Configuración

python3 manage.py migrate

python3 manage.py createsuperuser

# Ejecutar

python3 scrapping/manage.py runserver
