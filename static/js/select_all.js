window.onload = function() {
    django.jQuery('select[multiple]').each(function(){
        var select = this;
        var option = document.createElement('option');
        option.innerHTML = 'Выбрать всех';
        option.value = '';
        select.prepend(option);
    });
    django.jQuery(document).on('change', 'select[multiple]', function() {
        if (this.value === '') {
            django.jQuery(this).find('option').prop('selected', true);
            django.jQuery(this).find('option:first').prop('selected', false);
        }
    });
}
