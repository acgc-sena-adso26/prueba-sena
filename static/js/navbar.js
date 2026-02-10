    const menu = document.getElementById('hamburguesa');
    const contenido = document.querySelector('.contenido');
    const despl = document.querySelector('.despl');
    if (menu && contenido && despl) {
        menu.addEventListener('click', () => {
            contenido.classList.toggle('activo');
            despl.classList.toggle('activo');
        });
    }

    const logo = document.querySelector('.logo');
    const usuario = document.querySelector('.usuario');
    if (logo && usuario) {
        logo.addEventListener('click', () => {
            usuario.classList.toggle('activo');
        });
    }

    const flashes = document.querySelectorAll('.flash');
    if (flashes.length) {
        setTimeout(() => {
            flashes.forEach((flash) => flash.classList.add('hide'));
        }, 3500);
        setTimeout(() => {
            flashes.forEach((flash) => flash.remove());
        }, 4200);
    }
