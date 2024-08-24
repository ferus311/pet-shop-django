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

    async function updatePrice(productId, size, color, $priceElement) {
        let priceText = $priceElement.text();
        await $.ajax({
            url: '/get-price/',
            method: 'GET',
            data: {
                product_id: productId,
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
            error: function (xhr, status, error) {
                let errorMessage = 'Error fetching price';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                $priceElement.text(errorMessage);
            },
        });
    }

    async function filterOptions() {
        const productId = $('#price').data('product-id');
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


                updatePrice(productId, selectedSize, selectedColor, $priceElement) ;
            },
            error: function (error) {
                console.error('Error fetching available options:', error);
            },
        });
    }


    $sizeSelect.on('change', filterOptions);
    $colorSelect.on('change', filterOptions);

    const currentPath = window.location.pathname;
    const productDetailPattern = /^\/product\/\d+\/$/;
    if (productDetailPattern.test(currentPath)) {
        filterOptions();
    }

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
        if (number === undefined || number === null) {
            return '0';
        }
        return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function updateCartQuantity(action, itemId, quantity = null) {
        const data = {
            'item_id': itemId,
            'action': action,
            'csrfmiddlewaretoken': getCookie('csrftoken')
        };
        if (quantity !== null) {
            data.quantity = quantity;
        }

        $.ajax({
            url: '/update-quantity/',
            type: 'POST',
            data: data,
            success: function(response) {
                if (response.success) {
                    const quantityInput = $(`#quantity-${itemId}`);
                    const totalElement = $(`#total-${itemId}`);
                    const errorMessage = $(`#error-message-${itemId}`);

                    if (response.removed) {
                        $('#row-' + itemId).remove();
                    } else {
                        quantityInput.val(response.quantity);
                        totalElement.text(formatNumberWithCommas(response.total) + ' VND');
                    }

                    $('#subtotal').text(formatNumberWithCommas(response.subtotal) + ' VND');
                    $('#total_price').text(formatNumberWithCommas(response.total_price) + ' VND');
                    $('#discount_fee').text(formatNumberWithCommas(response.discount_fee) + ' VND');
                } else {
                    console.log(response.error);
                    location.reload();
                }
            },
            error: function(xhr, errmsg, err) {
                const errorMessage = $(`#error-message-${itemId}`);
                errorMessage.text(`Error: ${errmsg}`);
                location.reload();
            }
        });
    }

    // Lắng nghe sự kiện click cho nút tăng và giảm
    $('.btn-plus, .btn-minus').on('click', function() {
        const itemId = $(this).data('item-id');
        const action = $(this).data('action');
        updateCartQuantity(action, itemId);
    });

    // Lắng nghe sự kiện thay đổi cho input số lượng
    $('.quantity-input').on('change', function() {
        const itemId = $(this).data('item-id');
        const newQuantity = parseInt(this.value, 10);
        updateCartQuantity('update_quantity', itemId, newQuantity);
    });

    $('.remove-item').on('click', function() {
        const itemId = $(this).data('item-id');
        const $button = $(this);
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
                    $button.closest('tr').remove();
                    $('#subtotal').text(`${formatNumberWithCommas(response.subtotal)} VND`);
                    $('#total_price').text(`${formatNumberWithCommas(response.total_price)} VND`);
                    $('#discount_fee').text(`${formatNumberWithCommas(response.discount_fee)} VND`);
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
        const productId = $priceElement.data('product-id');

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

                updatePrice(productId, selectedSize, selectedColor, $priceElement);

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

    function addToCardFromModal(){
        let productDetails = [];
        var defaultPrice;
        function loadOptions(productId) {
            $.ajax({
                url: '/get-options-for-cart-modal/',
                data: {
                    product_id: productId
                },
                success: function(response) {
                    productDetails = response.product_details;
                    resetOptions();
                    updateOptions();
                    displayPrice();
                },
                error: function() {
                    alert('Failed to load options.');
                }
            });
        }

        function resetOptions() {
            $('#size-options').empty();
            $('#color-options').empty();
            $('#size-select-label').hide();
            $('#color-select-label').hide();
            $('.price-wrapper').text('');
            $("#submit-add-to-cart-btn").prop("disabled", true);
        }

        function updateOptions() {
            const sizeOptions = new Set();
            const colorOptions = new Set();
            let hasSizeOptions = false;
            let hasColorOptions = false;

            productDetails.forEach(detail => {
                if (detail.size) {
                    sizeOptions.add(detail.size.trim().toLowerCase());
                    hasSizeOptions = true;
                }
                if (detail.color) {
                    colorOptions.add(detail.color.trim().toLowerCase());
                    hasColorOptions = true;
                }
            });

            if (hasSizeOptions) {
                $('#size-options').empty();
                sizeOptions.forEach(size => {
                    $('#size-options').append(`<div class="option" data-size="${size}">${size}</div>`);
                });
                $('#size-select-label').show();
            } else {
                $('#size-select-label').hide();
            }

            if (hasColorOptions) {
                $('#color-options').empty();
                colorOptions.forEach(color => {
                    $('#color-options').append(`<div class="option" data-color="${color}">${color}</div>`);
                });
                $('#color-select-label').show();
            } else {
                $('#color-select-label').hide();
            }
            if (!hasSizeOptions && !hasColorOptions) {
                $('.price-wrapper').text(defaultPrice);
                $("#submit-add-to-cart-btn").prop("disabled", false);
                $('#product_detail_id').val(productDetails[0].id);

            }
        }

        $('#addToCartModal').on('show.bs.modal', function(event) {
            const button = $(event.relatedTarget);
            const productId = button.data('product-id');
            defaultPrice = button.data('default-price');
            loadOptions(productId);
        });

        $(document).on('click', '#size-options .option', function() {
            const $this = $(this);
            const selectedSize = $this.data('size');

            if ($this.hasClass('selected')) {
                $this.removeClass('selected');
                $('#color-options .option').removeClass('d-none');
                updatePrice();
            } else {
                $('#size-options .option').removeClass('selected');
                $this.addClass('selected');
                updateAvailableColors(selectedSize);
                updatePrice();
            }
        });

        $(document).on('click', '#color-options .option', function() {
            const $this = $(this);
            const selectedColor = $this.data('color');

            if ($this.hasClass('selected')) {
                $this.removeClass('selected');
                $('#size-options .option').removeClass('d-none');
                updatePrice();
            } else {
                $('#color-options .option').removeClass('selected');
                $this.addClass('selected');
                updateAvailableSizes(selectedColor);
                updatePrice();
            }
        });

        function updateAvailableColors(selectedSize) {
            $('#color-options .option').each(function() {
                const color = $(this).data('color');
                $(this).toggleClass('d-none', selectedSize && !isColorAvailable(selectedSize, color));
            });
        }

        function updateAvailableSizes(selectedColor) {
            $('#size-options .option').each(function() {
                const size = $(this).data('size');
                $(this).toggleClass('d-none', selectedColor && !isSizeAvailable(selectedColor, size));
            });
        }

        function isColorAvailable(size, color) {
            size = size.trim().toLowerCase();
            color = color.trim().toLowerCase();
            return productDetails.some(detail => detail.size && detail.size.trim().toLowerCase() === size && detail.color && detail.color.trim().toLowerCase() === color);
        }

        function isSizeAvailable(color, size) {
            size = size.trim().toLowerCase();
            color = color.trim().toLowerCase();
            return productDetails.some(detail => detail.color && detail.color.trim().toLowerCase() === color && detail.size && detail.size.trim().toLowerCase() === size);
        }

        function updatePrice() {
            const selectedSize = $('#size-options .option.selected').data('size');
            const selectedColor = $('#color-options .option.selected').data('color');
            const detail = productDetails.find(d =>
                (!d.size || d.size.trim().toLowerCase() === selectedSize) &&
                (!d.color || d.color.trim().toLowerCase() === selectedColor)
            );

            if (detail) {
                console.log(detail);
                $('.price-wrapper').text( detail.price);
                $('#product_detail_id').val(detail.id);
                $("#submit-add-to-cart-btn").prop("disabled", false);
            }
        }
        function displayPrice() {
            if (productDetails.length > 0) {
                $('.price-wrapper').text(defaultPrice);
            }
        }
        $('#submit-add-to-cart-btn').on('click', function(event) {
            const productDetailId = $('#product_detail_id').val();
            const quantity = $('#quantity').val() || 1;
            $.ajax({
                type: 'POST',
                url: '/add-to-cart/',
                data: {
                    'product_detail_id': productDetailId,
                    'quantity': quantity,
                },
                success: function(response) {
                    location.reload();
                },
                error: function(error) {
                    console.error('Error adding item to cart:', error);
                    location.reload();
                }
            });

        });


    }
    addToCardFromModal();


    function fetchAvailableVouchers() {
        $.ajax({
            url: '/get_available_vouchers/',
            type: 'GET',
            success: function(response) {
                const vouchers = response.vouchers;
                const voucherSelect = $('#voucher-select');
                const selectVoucherText = voucherSelect.data('select-voucher');
                const forEveryoneText = voucherSelect.data('for-everyone');
                const specialForYouText = voucherSelect.data('special-for-you');

                voucherSelect.empty();
                voucherSelect.append('<option value="" data-discount="0">' + selectVoucherText + '</option>');

                vouchers.forEach(function(voucher) {
                    const categories = voucher.categories.join(', ');
                    const formattedDiscount = voucher.discount.toLocaleString('en-US');
                    const availability = voucher.is_global ? forEveryoneText : specialForYouText;
                    const minAmount = voucher.min_amount.toLocaleString('en-US');
                    const optionText = categories + ' - ' + formattedDiscount + '%' + availability + ' - Min: ' + minAmount + ' VND';

                    const option = $('<option></option>')
                        .val(voucher.id)
                        .data('discount', voucher.discount)
                        .data('minAmount', voucher.min_amount)
                        .data('categories', categories)
                        .data('is_global', voucher.is_global)
                        .html(optionText);

                    voucherSelect.append(option);
                });
                vouchersFetched = true;
            },
            error: function(error) {
                console.error('Error fetching vouchers:', error);
            }
        });
    }
    let vouchersFetched = false;
    $('#voucher-select').on('click', function() {
        if (!vouchersFetched) {
            fetchAvailableVouchers();
        }
    });

    $('#apply-voucher').click(function() {
        try {
            const voucherId = $('#voucher-select').val();
            const discount = $('#voucher-select option:selected').data('discount');
            const minAmount = $('#voucher-select option:selected').data('minAmount');
            const subtotalText = $('#subtotal').text().replace(/,/g, '');
            const subtotal = parseFloat(subtotalText);

            const shippingFeeText = $('#shipping_fee').text().replace(/[^0-9.]/g, '');
            const shippingFee = parseFloat(shippingFeeText);

            $.ajax({
                url: '/apply_voucher/',
                type: 'POST',
                data: {
                    'voucher_id': voucherId,
                    'subtotal': subtotal,
                    'min_amount': minAmount,
                    'csrfmiddlewaretoken': getCookie('csrftoken')
                },
                success: function(response) {
                    if (response.success) {
                        if (subtotal >= minAmount) {
                            const discount_fee = response.discount_amount;
                            const totalPrice = response.final_price + shippingFee;
                            $('#discount_fee').text('-' + formatPrice(discount_fee) + ' VND');
                            $('#total_price').text(formatPrice(totalPrice) + ' VND');
                        } else {
                            location.reload();
                        }
                    } else {
                        location.reload();
                    }
                },
                error: function(error) {
                    console.error('Error applying voucher:', error);
                }
            });
        } catch (error) {
            console.error('An error occurred:', error);
            alert('An unexpected error occurred. Please try again later.');
        }
    });

    $('form').on('submit', function(event) {
        const cancelButton = $(this).find('.cancel-item');
        if (cancelButton.length) {
            event.preventDefault();
            const confirmationMessage = cancelButton.data('cancel-confirmation');
            const confirmation = confirm(confirmationMessage);
            if (confirmation) {
                this.submit();
            }
        }
    });
    window.changeLanguage = function(languageCode) {
        const $form = $('#languageForm');
        $form.find('input[name="language"]').val(languageCode);

        document.body.classList.remove('english-font', 'vietnamese-font');

        if (languageCode === 'en') {
            document.body.classList.add('english-font');
        } else if (languageCode === 'vi') {
            document.body.classList.add('vietnamese-font');
        }

        $form.submit();
    }


    $('.form').on('submit', function(event) {
        let allValid = true;

        $('input.required').each(function() {
            const $input = $(this);
            const $errorMessage = $input.next('.error-message');
            if ($input.val().trim() === '') {
                allValid = false;
                $errorMessage.show();
                $input.addClass('error');
            } else {
                $input.removeClass('error');
                $errorMessage.hide();
            }
        });

        if (!allValid) {
            event.preventDefault();
        }
    });

    $('input.required').on('blur', function() {
        const $input = $(this);
        const $errorMessage = $input.next('.error-message');
        if ($input.val().trim() === '') {
            $input.addClass('error');
            $errorMessage.show();
        } else {
            $input.removeClass('error');
            $errorMessage.hide();
        }
    });
    $('.btn-cart').on('click', function() {
        var productId = $(this).data('product-id');
        $('#addToCartModal' + productId).modal('show');
    });
})(jQuery);
