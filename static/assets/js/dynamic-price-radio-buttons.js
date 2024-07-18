// script.js

$(document).ready(function() {
    // When a radio button is selected
    $('input[type="radio"]').on('change', function() {
        var salePrice = $(this).data('sale-price');
        var retailPrice = $(this).data('retail-price');
        
        $('#sale-price').text('$ ' + salePrice);
        $('#retail-price').text('$ ' + retailPrice);
    });

    // Select the first radio button by default
    $('input[type="radio"]:first').prop('checked', true).trigger('change');
});
