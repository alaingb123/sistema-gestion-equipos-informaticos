# Sistema de Gestión de Equipos Informáticos

## Descripción
Este es un sistema de gestión de equipos informáticos desarrollado en Django que permite administrar y dar seguimiento a diferentes componentes de hardware, estaciones de trabajo y periféricos dentro de una empresa o entidad.

## Estructura del Proyecto
El proyecto está organizado en las siguientes aplicaciones principales:
- `EquiposInformaticos/`: Configuración principal del proyecto Django
- `ComponentesInternos/`: Gestión de componentes internos de hardware
- `EstacionesTrabajo/`: Administración de estaciones de trabajo
- `Perifericos/`: Control de periféricos y dispositivos externos

## Requisitos del Sistema
- Python 3.x
- Django 5.1.6
- Otras dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la base de datos:
```bash
python manage.py migrate
```

5. Crear un superusuario:
```bash
python manage.py createsuperuser
```

6. Iniciar el servidor de desarrollo:
```bash
python manage.py runserver
```

## Características Principales
- Gestión de componentes internos de hardware
- Administración de estaciones de trabajo
- Control de periféricos
- Importación/Exportación de datos (usando django-import-export)
- Filtros avanzados en el panel de administración
- Soporte para archivos Excel (procesador.xlsx, sistemas.xlsx)

## Estructura de Archivos
- `manage.py`: Script de administración de Django
- `requirements.txt`: Lista de dependencias del proyecto
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `templates/`: Plantillas HTML
- `media/`: Archivos multimedia subidos por usuarios
- `staticfiles/`: Archivos estáticos recolectados para producción

## Guías de Despliegue
El proyecto incluye dos guías de despliegue:
- `Guia para despliegue 1.0.txt`: Versión inicial de la guía
- `Guia para despliegue en produccion 1.1.txt`: Guía actualizada para despliegue en producción

## Base de Datos
El proyecto utiliza SQLite como base de datos por defecto (`db.sqlite3`). Para entornos de producción, se recomienda migrar a PostgreSQL o MySQL.

## Contribución
1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia
Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

La Licencia MIT es una licencia de software permisiva que permite:
- Uso comercial
- Modificación
- Distribución
- Uso privado

Con las siguientes condiciones:
- Incluir el aviso de copyright original
- Incluir la licencia MIT

## Contacto
alaingalvez76@gmail.com