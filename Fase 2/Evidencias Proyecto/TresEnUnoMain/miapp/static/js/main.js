(function ($) {
    "use strict";
    
    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('onMouseOut', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('onMouseOut');
            }
        }
        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Facts counter
    $('[data-toggle="counter-up"]').counterUp({
        delay: 10,
        time: 2000
    });


    // Courses carousel
    $(".courses-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        loop: true,
        dots: false,
        nav : false,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:2
            },
            768:{
                items:3
            },
            992:{
                items:4
            }
        }
    });


    // Team carousel
    $(".team-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 30,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="fa fa-angle-left" aria-hidden="true"></i>',
            '<i class="fa fa-angle-right" aria-hidden="true"></i>'
        ],
        responsive: {
            0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="fa fa-angle-left" aria-hidden="true"></i>',
            '<i class="fa fa-angle-right" aria-hidden="true"></i>'
        ],
    });


    // Related carousel
    $(".related-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        margin: 30,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="fa fa-angle-left" aria-hidden="true"></i>',
            '<i class="fa fa-angle-right" aria-hidden="true"></i>'
        ],
        responsive: {
            0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            }
        }
    });
    
})(jQuery);

// Segundo bloque de OWL Carousel
$('.owl-carousel').owlCarousel({
    loop: true,
    margin: 20,
    nav: true,
    responsive: {
        0: {
            items: 1
        },
        576: {
            items: 2
        },
        768: {
            items: 3
        },
        992: {
            items: 4
        }
    }
}); 

// ==========================================================
// LÓGICA DE AUTENTICACIÓN Y CIERRE DE SESIÓN 🔑
// ==========================================================

const API_BASE_URL = 'http://127.0.0.1:8000';

// Función para limpiar el token y cerrar la sesión
function logoutClient(event) {
    event.preventDefault(); 
    localStorage.removeItem('accessToken');
    
    // ⭐ Truco para forzar la recarga y evitar el caché del navegador en el logout
    window.location.replace(window.location.origin + '?logout=' + Date.now()); 
}

// Función que verifica el estado del login y actualiza la barra
async function updateNavbarAuthStatus() {
    const accessToken = localStorage.getItem('accessToken');
    const guestDiv = document.getElementById('auth-guest');
    const userDiv = document.getElementById('auth-user');
    const userNameDisplay = document.getElementById('userNameDisplay');

    // ⭐ CAMBIO CRÍTICO: Limpieza inicial forzada por clases (d-none)
    // Esto resuelve el problema de ver los dos botones al mismo tiempo.
    if (guestDiv) {
        guestDiv.classList.add('d-none');
        guestDiv.classList.remove('d-flex');
    }
    if (userDiv) {
        userDiv.classList.add('d-none');
        userDiv.classList.remove('d-flex');
    }

    if (accessToken) {
        try {
            // 1. Verificar si el token es válido
            const verifyResponse = await fetch(`${API_BASE_URL}/api/auth/verify-token`, {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });

            if (verifyResponse.ok) {
                // 2. Si es válido, obtener los datos del cliente
                const userResponse = await fetch(`${API_BASE_URL}/api/clientes/me`, { 
                    method: 'GET',
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                
                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    if (userNameDisplay) {
                        userNameDisplay.textContent = userData.nombre || userData.correo || 'Mi Cuenta'; 
                    }
                    // MUESTRA EL DE USUARIO: Remueve d-none y deja que d-flex se aplique
                    if (userDiv) {
                        userDiv.classList.remove('d-none');
                    }

                } else {
                    // MUESTRA EL DE INVITADO: Token válido, pero falló obtener datos.
                    localStorage.removeItem('accessToken');
                    if (guestDiv) {
                        guestDiv.classList.remove('d-none');
                    }
                }

            } else {
                // MUESTRA EL DE INVITADO: Token inválido (401).
                localStorage.removeItem('accessToken');
                if (guestDiv) {
                    guestDiv.classList.remove('d-none');
                }
            }
        } catch (error) {
            console.error("Error de conexión:", error);
            localStorage.removeItem('accessToken');
            // MUESTRA EL DE INVITADO: Error de conexión
            if (guestDiv) {
                guestDiv.classList.remove('d-none');
            }
        }

    } else {
        // MUESTRA EL DE INVITADO: No hay token.
        if (guestDiv) {
            guestDiv.classList.remove('d-none');
        }
    }
}


// BLOQUE DE EJECUCIÓN (Asegúrate de que este bloque también esté al final de tu main.js)
$(document).ready(function() {
    // 1. Ejecutar la verificación de autenticación al cargar la página
    updateNavbarAuthStatus();

    // 2. Adjuntar el listener de Logout
    $('#logout-link').on('click', logoutClient);
});