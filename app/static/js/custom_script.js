(function ($) {
    "use strict";

    window.addEventListener('load', function () {
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
        return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    async function updatePrice(size, color, $priceElement) {
        await $.ajax({
            url: '/get-price/',
            method: 'GET',
            data: {
                size: size,
                color: color || 'None'
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
                    $priceElement.text('0 VND');
                }
                if ($priceElement && $priceElement.attr('id')) {
                    const itemId = $priceElement.attr('id').split('-').pop();
                    updateTotalPrice(itemId);
                }
            },
            error: function (error) {
                console.error('Error fetching price:', error);
                $priceElement.text('Error fetching price');
            },
        });
    }

    async function filterOptions() {
        const selectedSize = $sizeSelect.val();
        const selectedColor = $colorSelect.val();
        $.ajax({
            url: '/get-available-options/',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                const availableSizes = data.sizes || [];
                const availableColors = data.colors || [];

                $sizeSelect.find('option').each(function () {
                    const optionValue = $(this).val();
                    $(this).prop(
                        'disabled',
                        !availableSizes.includes(optionValue)
                    );
                });

                $colorSelect.find('option').each(function () {
                    const optionValue = $(this).val();
                    $(this).prop(
                        'disabled',
                        !availableColors.includes(optionValue)
                    );
                });


                updatePrice(selectedSize, selectedColor, $priceElement) ;
            },
            error: function (error) {
                console.error('Error fetching available options:', error);
            },
        });
    }


    $sizeSelect.on('change', filterOptions);
    $colorSelect.on('change', filterOptions);

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

    function checkFoucusSearch () {
        var timeout;

        function search_header() {
            $('#query-header-search').on('focus', function() {
                var query = $(this).val();

                clearTimeout(timeout);

                if (query.length === 0) {
                    timeout = setTimeout(function() {
                        $.ajax({
                            url: '/search-products/',
                            method: 'GET',
                            dataType: 'json',
                            data: {
                                query: ''
                            },
                            success: function(data) {
                                var results = $('#search-results');
                                results.empty();
                                if (data.results.length > 0) {
                                    data.results.forEach(function(item) {
                                        results.append(
                                            '<li class="list-group-item">' +
                                                '<a href="/product/' +
                                                    item.id +
                                                    '">' +
                                                    item.name +
                                                '</a>' +
                                            '</li>'
                                        );
                                    });
                                } else {
                                    results.append(
                                        '<li class="list-group-item">No products found</li>'
                                    );
                                }
                            }
                        });
                    }, 100);
                }
            });

            $('#query-header-search').on('input', function() {
                var query = $(this).val();

                clearTimeout(timeout);

                timeout = setTimeout(function() {
                    if (query.length > 0) {
                        $.ajax({
                            url: '/search-products/',
                            method: 'GET',
                            dataType: 'json',
                            data: {
                                query: query
                            },
                            success: function(data) {
                                var results = $('#search-results');
                                results.empty();
                                if (data.results.length > 0) {
                                    data.results.forEach(function(item) {
                                        results.append(
                                            '<li class="list-group-item">' +
                                                '<a href="/product/' +
                                                    item.id +
                                                    '">' +
                                                    item.name +
                                                '</a>' +
                                            '</li>'
                                        );
                                    });
                                } else {
                                    results.append(
                                        '<li class="list-group-item">No products found</li>'
                                    );
                                }
                            }
                        });
                    } else {
                        $.ajax({
                            url: '/search-products/',
                            method: 'GET',
                            dataType: 'json',
                            data: {
                                query: ''
                            },
                            success: function(data) {
                                var results = $('#search-results');
                                results.empty();
                                if (data.results.length > 0) {
                                    data.results.forEach(function(item) {
                                        results.append(
                                            '<li class="list-group-item">' +
                                                '<a href="/product/' +
                                                    item.id +
                                                    '">' +
                                                    item.name +
                                                '</a>' +
                                            '</li>'
                                        );
                                    });
                                } else {
                                    results.append(
                                        '<li class="list-group-item">No products found</li>'
                                    );
                                }
                            }
                        });
                    }
                }, 100);
            });

            $('#query-header-search, #search-results').on('focusout', function(event) {
                setTimeout(function() {
                    if (!$('#query-header-search').is(':focus') && !$('#search-results').is(':focus')) {
                        $('#search-results').empty();
                    }
                }, 0);
            });

            $('#search-results').on('mousedown', 'a', function(event) {
                event.preventDefault();
            });
        }

        search_header();
    };
    checkFoucusSearch();


    function formatNumberWithCommas(number) {
        return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    $('.btn-plus, .btn-minus').on('click', function() {
        const itemId = $(this).data('item-id');
        const action = $(this).data('action');
        const quantityInput = $(`#quantity-${itemId}`);
        const totalElement = $(`#total-${itemId}`);
        const subtotalElement = $('#subtotal');
        const totalPriceElement = $('#total_price');
        const errorMessage = $(`#error-message-${itemId}`);

        $.ajax({
            url: '/update-quantity/',
            type: 'POST',
            data: {
                'item_id': itemId,
                'action': action,
                'csrfmiddlewaretoken': getCookie('csrftoken')
            },
            success: function(response) {
                if (response.success) {
                    if (response.removed) {
                        $(`#cart-item-${itemId}`).remove();
                        location.reload();
                    } else {
                        quantityInput.val(response.quantity);
                        totalElement.text(formatNumberWithCommas(response.total) + ' VND');
                    }
                    subtotalElement.text(formatNumberWithCommas(response.subtotal) + ' VND');
                    totalPriceElement.text(formatNumberWithCommas(response.total_price) + ' VND');
                } else {
                    errorMessage.text(response.error);
                    location.reload();
                }
            },
            error: function(xhr, errmsg, err) {
                errorMessage.text(`Error: ${errmsg}`);
                location.reload();
            }
        });
    });

    $('.remove-item').on('click', function() {
        const itemId = $(this).data('item-id');
        $.ajax({
            url: `/cart/remove/${itemId}/`,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            data: JSON.stringify({
                'item_id': itemId,
            }),
            contentType: 'application/json',
            success: function(response) {
                if (response.success) {
                    $(`#cart-item-${itemId}`).remove();
                    $('#subtotal').text(`${response.subtotal} VND`);
                    $('#total-price').text(`${response.total_price} VND`);
                    location.reload();
                } else {
                    console.log('An error occurred while removing the item:', response.error);
                }
            },
            error: function() {
                console.log(`Error: ${errmsg}`);
            }
        });
    });

    async function updateSubtotal() {
        let subtotal = 0;

        $('[id^="total-"]').each(function() {
            const totalText = $(this).text().replace(/[^0-9.]/g, '');
            const total = parseFloat(totalText);
            if (!isNaN(total)) {
                subtotal += total;
            }
        });
        $('#subtotal').text(formatPrice(subtotal) + ' VND');
    }

    async function updateTotalPrice(itemId) {
        const $quantityElement = $(`#quantity-${itemId}`);
        const $priceElement = $(`#price-${itemId}`);
        const $totalElement = $(`#total-${itemId}`);

        const quantity = parseInt($quantityElement.val(), 10);
        const priceText = $priceElement.text().replace(/[^0-9]/g, '');
        const price = parseFloat(priceText);

        if (isNaN(price) || isNaN(quantity)) {
            $totalElement.text('0 VND');
            return;
        }

        const total = price * quantity;
        $totalElement.text(formatPrice(total) + ' VND');

        await updateSubtotal();
        const subtotalText = $('#subtotal').text().replace(/[^0-9.]/g, '');
        const shippingFeeText = $('#shipping_fee').text().replace(/[^0-9.]/g, '');
        const discountFeeText = $('#discount_fee').text().replace(/[^0-9.]/g, '');
        const subtotal = parseFloat(subtotalText);
        const shippingFee = parseFloat(shippingFeeText);
        const discountFee = parseFloat(discountFeeText);

        if (isNaN(subtotal) || isNaN(shippingFee) || isNaN(discountFee)) {
            console.error('Invalid subtotal, shipping fee, or discount fee:', subtotal, shippingFee, discountFee);
            $('#total_price').text('0 VND');
            return;
        }

        const totalPrice = subtotal + (isNaN(shippingFee) ? 0 : shippingFee) - (isNaN(discountFee) ? 0 : discountFee);
        $('#total_price').text(formatPrice(totalPrice) + ' VND');
    }

    async function handleUpdateCartPrice(itemId) {
        const $sizeSelect = $(`#size-select-${itemId}`);
        const $colorSelect = $(`#color-select-${itemId}`);
        const $priceElement = $(`#price-${itemId}`);

        const selectedSize = $sizeSelect.val();
        const selectedColor = $colorSelect.val();

        await $.ajax({
            url: '/get-available-options/',
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                const availableSizes = data.sizes || [];
                const availableColors = data.colors || [];

                $sizeSelect.find('option').each(function () {
                    const optionValue = $(this).val();
                    $(this).prop(
                        'disabled',
                        !availableSizes.includes(optionValue)
                    );
                });

                $colorSelect.find('option').each(function () {
                    const optionValue = $(this).val();
                    $(this).prop(
                        'disabled',
                        !availableColors.includes(optionValue)
                    );
                });

                updatePrice(selectedSize, selectedColor, $priceElement);

                $.ajax({
                    url: '/update-cart-item/',
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    contentType: 'application/json',
                    data: JSON.stringify({
                        item_id: itemId,
                        quantity: $(`#quantity-${itemId}`).val(),
                        size: selectedSize,
                        color: selectedColor
                    }),
                    success: function (response) {
                        console.log('Cart item updated successfully:', response.message);
                    },
                    error: function (error) {
                        console.error('Error updating cart item:', error);
                        location.reload(true);
                    }
                });
            },
            error: function (error) {
                console.error('Error fetching available options:', error);
                location.reload(true);
            },
        });
    }

    $('select[id^="size-select-"], select[id^="color-select-"], input[id^="quantity-"]').on('change', function () {
        const itemId = this.id.split('-').pop();
        handleUpdateCartPrice(itemId);
    });

    $('#payment-method-select').on('change', function() {
        var visaCardInfo = $('#visa-card-info');
        if ($(this).val() === 'Transfer') {
            visaCardInfo.show();
        } else {
            visaCardInfo.hide();
        }
    })


    $('#image').off('change').on('change', function(event) {
        const preview = $('#imagePreview');
        preview.empty();
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = $('<img>', {
                src: e.target.result,
                class: 'img-preview'
            });
            const removeBtn = $('<span>', {
                text: 'Xóa ảnh',
                class: 'remove-btn'
            }).on('click', function() {
                img.remove();
                removeBtn.remove();
                $('#image').val('');
            });
            preview.append(img).append(removeBtn);
        };
        reader.readAsDataURL(file);
    });

    $('#reviewModal').on('show.bs.modal', function(event) {
        const button = $(event.relatedTarget);
        const productId = button.data('product-id');
        const modal = $(this);
        modal.find('#product_id').val(productId);
    });

})(jQuery);
