django.jQuery(function($) {
    $(document).ready(function() {
        $('.admin-filter select').on('change', function() {
            var $select = $(this);
            var $form = $select.closest('form');
            $form.submit();
        });
    });
}); 