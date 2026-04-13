from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comicon.urls')),  # Sostituisci 'myapp' con il nome reale della tua app
]
