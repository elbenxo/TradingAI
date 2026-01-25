// Navegación móvil
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Cerrar menú al hacer clic en un enlace
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });

    // Cambiar estilo del navbar al hacer scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.padding = '10px 0';
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.padding = '15px 0';
            navbar.style.boxShadow = 'none';
        }
    });

    // Formulario de contacto
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const nombre = document.getElementById('nombre').value;
            const email = document.getElementById('email').value;
            const mensaje = document.getElementById('mensaje').value;

            // Aquí puedes integrar con un servicio como Formspree, EmailJS, etc.
            // Por ahora, mostramos un mensaje y abrimos el cliente de email

            const mailtoLink = `mailto:teleco25vigo@gmail.com?subject=Contacto 25 Aniversario - ${encodeURIComponent(nombre)}&body=${encodeURIComponent(mensaje)}%0A%0AContacto: ${encodeURIComponent(email)}`;

            window.location.href = mailtoLink;

            // Alternativa: mostrar mensaje de confirmación
            // alert('¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.');
            // contactForm.reset();
        });
    }

    // Animación suave para los elementos al hacer scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Aplicar animación a las tarjetas y elementos
    document.querySelectorAll('.evento-card, .galeria-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Función para añadir fotos a la galería (útil para los colaboradores)
function addPhotoToGallery(imageUrl, altText) {
    const galleryGrid = document.querySelector('.galeria-grid');
    const placeholder = galleryGrid.querySelector('.galeria-placeholder');

    if (placeholder) {
        const parent = placeholder.parentElement;
        parent.innerHTML = `<img src="${imageUrl}" alt="${altText || 'Foto de la promoción'}">`;
    }
}

// Ejemplo de uso:
// addPhotoToGallery('img/foto1.jpg', 'Graduación 2000');
