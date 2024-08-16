(function ($) {
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
                color: selectedColor || 'None'
            },
            dataType: 'json',
            success: function (data) {
                if (data.price) {
                    const formattedPrice = formatPrice(data.price);
                    $priceElement.text(`${formattedPrice} VND`);
                } else if (data.product_price) {
                    const formattedProductPrice = formatPrice(data.product_price);
                    $priceElement.text(`${formattedProductPrice} VND`);
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

    async function getProductDetailId(productId, selectedColor, selectedSize) {
        try {
            const response = await $.ajax({
                type: 'GET',
                url: '/get-product-detail-id/',
                data: {
                    'product_id': productId,
                    'color': selectedColor,
                    'size': selectedSize
                }
            });
            if (response.product_detail_id) {
                return response.product_detail_id;
            } else {
                return null;
            }
        } catch (error) {
            console.error('Error fetching product detail ID:', error);
            return null;
        }
    }

    $('.add-to-cart').on('click', async function(event) {
        event.preventDefault();

        const productId = $(this).data('product-id');
        const selectedColor = $('#color-select').val();
        const selectedSize = $('#size-select').val();
        const quantity = $(this).data('quantity');

        try {
            const productDetailId = await getProductDetailId(productId, selectedColor, selectedSize);

            $.ajax({
                type: 'POST',
                url: '/add-to-cart/',
                data: {
                    'product_detail_id': productDetailId,
                    'quantity': quantity,
                    'csrfmiddlewaretoken': getCookie('csrftoken')
                },
                success: function(response) {
                    console.log('Item added to cart:', response);
                    location.reload();
                },
                error: function(error) {
                    console.error('Error adding item to cart:', error);
                    location.reload();
                }
            });
        } catch (error) {
            console.error('Error fetching product ID:', error);
        }
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    (function($) {
        $('#rangeInput').on('input', function() {
            $('#amount').val($(this).val());
        });

        $('#amount').on('input', function() {
            $('#rangeInput').val($(this).val());
        });

        $('#rangeInput, #amount').on('change', function() {
            $('#priceFilterForm').submit();
        });
    });

})(jQuery);
