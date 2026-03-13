# core/create_superuser.py

import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and password:
    if not User.objects.filter(username=username).exists():
        print("Creando superusuario automáticamente...")
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
    else:
        print("El superusuario ya existe.")