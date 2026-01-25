# 2001: Odisea en el Cuvi - 25 Aniversario

Web para el 25 aniversario de la promocion de Ingenieros de Telecomunicaciones de la Universidad de Vigo (Promocion 2001).

## Ver la web

**https://elbenxo.github.io/teleco-vigo-25/**

## El Evento

- **Fecha:** Sabado 7 de Noviembre de 2026
- **Lugar:** Palacio de La Oliva, Vigo
- **Horario:** 14:00 - 20:00
- **Precio estimado:** ~87€ (sin barra libre) / ~100€ (con barra libre)

## Como colaborar

### 1. Clonar el repositorio

```bash
git clone https://github.com/elbenxo/teleco-vigo-25.git
cd teleco-vigo-25
```

### 2. Estructura del proyecto

```
teleco-vigo-25/
├── index.html      # Pagina principal
├── css/
│   └── styles.css  # Estilos visuales
├── js/
│   └── main.js     # Interactividad
├── img/            # Carpeta para fotos
└── README.md
```

### 3. Anadir fotos

1. Anade tus fotos a la carpeta `img/`
2. Edita `index.html` y busca la seccion de galeria
3. Reemplaza los placeholders:

```html
<!-- Antes -->
<div class="galeria-item">
    <div class="galeria-placeholder">...</div>
</div>

<!-- Despues -->
<div class="galeria-item">
    <img src="img/tu-foto.jpg" alt="Descripcion de la foto">
</div>
```

### 4. Subir cambios

```bash
git add .
git commit -m "Descripcion de los cambios"
git push
```

Los cambios se publicaran automaticamente en unos minutos.

## Como probar en local

Simplemente abre `index.html` en tu navegador.

Si quieres usar un servidor local:

```bash
# Con Python 3
python -m http.server 8000

# Con Node.js
npx serve
```

## Links utiles

- **Documento compartido:** [Google Sheets](https://docs.google.com/spreadsheets/d/1_vuDEwB8ZVF3fyHGsIH45cQyUbTn95LDGxBA-W3k63s/edit?gid=908705264#gid=908705264)
- **Palacio de La Oliva:** https://www.palaciodelaoliva.com/
- **Hotel AC Palacio Universal:** Para reservar, email a reception.palaciouniversal@achmhotels.com mencionando "REUNION INGENIEROS TELECOMUNICACIONES"

## Contacto

Para dudas sobre el evento, contactar a Jose Moar a traves del grupo de WhatsApp.
