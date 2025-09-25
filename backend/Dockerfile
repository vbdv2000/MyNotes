# Usa una imagen oficial de Python como base.
FROM python:3.11-slim

# Establece el directorio de trabajo en /app.
WORKDIR /app

# Copia los archivos de requerimientos e instálalos usando uv.
# El --system es para que no cree un entorno virtual dentro del contenedor.
COPY ./backend/requirements.txt .
RUN pip install uv
RUN uv pip install -r requirements.txt --system

# Copia el resto del código de la aplicación.
COPY ./backend/app /app/app

# Expón el puerto donde correrá Uvicorn.
EXPOSE 8000

# Define el comando para ejecutar la aplicación.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]