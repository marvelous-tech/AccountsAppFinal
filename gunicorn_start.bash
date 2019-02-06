NAME="django_app"
DJANGODIR=/home/ubuntu/project
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=project.settings
DJANGO_WSGI_MODULE=project.wsgi
echo "Starting $NAME as `whoami`"

# Activate the virtual machine

cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Start Django Gunicorn

exec pipenv run gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --bind=8000:8000 \
    --log-level=debug \
    --log-file=-
