$(document).ready(function ($) {
    "use strict";

    window.addEventListener("load", function () {
        const reviewLink = $('#review-link');
        const reviewTab = $('#nav-mission-tab');

        reviewLink.on('click', function (event) {
            event.preventDefault();
            reviewTab.click();
            $('#description-section')[0].scrollIntoView({ behavior: 'smooth' });
        });
    });

    const $sizeSelect = $('#size-select');
    const $colorSelect = $('#color-select');
    const $priceElement = $('#price');

    function formatPrice(price) {
        return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function updatePrice() {
        const selectedSize = $sizeSelect.val();
        const selectedColor = $colorSelect.val();

        $.ajax({
            url: '/get-price/',
            method: 'GET',
            data: {
                size: selectedSize,
                color: selectedColor
            },
            dataType: 'json',
            success: function (data) {
                if (data.price) {
                    const formattedPrice = formatPrice(data.price);
                    $priceElement.text(`${formattedPrice} VND`);
                } else {
                    $priceElement.text('N/A');
                }
            },
            error: function (error) {
                console.error('Error fetching price:', error);
                $priceElement.text('Error fetching price');
            }
        });
    }

    function filterOptions() {
        $.ajax({
            url: '/get-available-options/',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                const availableSizes = data.sizes || [];
                const availableColors = data.colors || [];

                $sizeSelect.find('option').each(function () {
                    const optionValue = $(this).val();
                    $(this).prop('disabled', !availableSizes.includes(optionValue));
                });

                $colorSelect.find('option').each(function () {
                    const optionValue = $(this).val();
                    $(this).prop('disabled', !availableColors.includes(optionValue));
                });

                // Update the price once the options are filtered
                updatePrice();
            },
            error: function (error) {
                console.error('Error fetching available options:', error);
            }
        });
    }

    $sizeSelect.on('change', updatePrice);
    $colorSelect.on('change', updatePrice);

    filterOptions();

})(jQuery);
