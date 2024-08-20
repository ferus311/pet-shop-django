(function($) {
    'use strict';
    var map;
    var marker;
    const defaultAddress = $('#default_user_address').val();
    const apiKey = OPENCAGE_API_KEY;

    function initializeMap(lat, lng) {
        if (map) {
            map.remove();
        }
        map = L.map('map').setView([lat, lng], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        marker = L.marker([lat, lng]).addTo(map);

        $('#latitude').val(lat);
        $('#longitude').val(lng);

        getAddress(lat, lng);

        map.on('click', function(e) {
            marker.setLatLng(e.latlng);
            $('#latitude').val(e.latlng.lat);
            $('#longitude').val(e.latlng.lng);

            getAddress(e.latlng.lat, e.latlng.lng);
        });
    }

    function getCoordinatesFromAddress(address, callback) {
        $.getJSON(`https://api.opencagedata.com/geocode/v1/json?q=${encodeURIComponent(address)}&key=${apiKey}`, function(data) {
            if (data.results.length > 0) {
                var lat = data.results[0].geometry.lat;
                var lng = data.results[0].geometry.lng;
                callback(lat, lng);
            } else {
                console.error('Geocoding failed: ' + data.status);
            }
        });
    }

    if (defaultAddress) {
        getCoordinatesFromAddress(defaultAddress, function(lat, lng) {
            initializeMap(lat, lng);
        });
    } else if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var userLat = position.coords.latitude;
            var userLng = position.coords.longitude;

            initializeMap(userLat, userLng);
        });
    } else {
        initializeMap(10.762622, 106.660172);
    }

    $('#location-form-button').on('click', function(e) {
        e.preventDefault();
        var location = $('#location-input').val();
        console.log('Location:', location);

        getCoordinatesFromAddress(location, function(lat, lng) {
            initializeMap(lat, lng);
        });
    });

    function getAddress(lat, lng) {
        $.getJSON(`https://api.opencagedata.com/geocode/v1/json?q=${lat}+${lng}&key=${apiKey}`, function(data) {
            if (data.results.length > 0) {
                $('#address').text(`Address: ${data.results[0].formatted}`);
            } else {
                $('#address').text("Address not found.");
            }
        }).fail(function(error) {
            console.error('Error fetching address:', error);
        });
    }

    $('#save-location-button').on('click', function(e) {

        var lat = $('#latitude').val();
        var lng = $('#longitude').val();

        var locationInputValue = $('#location-input').val();
        if (locationInputValue.length > 0) {
            $('#default_user_address').val(locationInputValue);
        }

        $('#selected-coordinates').text(`Selected Coordinates: Latitude ${lat}, Longitude ${lng}`);

    });
})(jQuery);
