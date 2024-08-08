$(document).ready(function() {
    $('.alert').each(function() {
        const $alert = $(this);
        setTimeout(function() {
            $alert.addClass('fade');
            setTimeout(function() {
                $alert.remove();
            }, 100);
        }, 2000);
    });
});
