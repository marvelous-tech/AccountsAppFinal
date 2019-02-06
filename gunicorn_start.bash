NAME="django_app"
DJANGODIR=/home/ubuntu/project
SOCKFILE=/run/gunicorn.sock
USER=ubuntu
GROUP=ubuntu
NUM_WORKERS=3
DJANGO_SETTINGS_MODULE=project.settings
DJANGO_WSGI_MODULE=project.wsgi
echo "Starting $NAME as `whoami`"

# Activate the virtual machine

cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

# Start Django Gunicorn

exec /usr/loacl/bin/pipenv run gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name $NAME \
    --workers $NUM_WORKERS \
    --user=$USER --group=$GROUP \
    --bind=unix:$SOCKFILE \
    --log-level=debug \
    --log-file=-

