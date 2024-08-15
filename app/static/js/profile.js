$(document).ready(function () {
    const originalValues = {};
    const mainInputs = $(".main-infor input");

    mainInputs.each(function () {
        originalValues[this.id] = $(this).val();
    });

    const cancelBtnMain = $(".main-infor .cancel-btn");
    if (cancelBtnMain.length) {
        cancelBtnMain.on("click", function (e) {
            e.preventDefault();
            mainInputs.each(function () {
                $(this).val(originalValues[this.id]);
            });
        });
    }

    const passwordInputs = $(".user-profile-password input[type='password']");
    const cancelBtnPassword = $(".user-profile-password .cancel-btn");

    if (cancelBtnPassword.length) {
        cancelBtnPassword.on("click", function (e) {
            e.preventDefault();
            passwordInputs.val("");
        });
    }
});

function previewImage() {
    const fileInput = document.getElementById('image');
    const file = fileInput.files[0];
    const imgPreview = document.getElementById('avatar-preview');

    if (file) {
        const reader = new FileReader();

        reader.onload = function(event) {
            imgPreview.src = event.target.result;
        };

        reader.readAsDataURL(file);
    }
}$(document).ready(function () {
    const originalValues = {};
    const mainInputs = $(".main-infor input");

    mainInputs.each(function () {
        originalValues[this.id] = $(this).val();
    });

    const cancelBtnMain = $(".main-infor .cancel-btn");
    if (cancelBtnMain.length) {
        cancelBtnMain.on("click", function (e) {
            e.preventDefault();
            mainInputs.each(function () {
                $(this).val(originalValues[this.id]);
            });
        });
    }

    const passwordInputs = $(".user-profile-password input[type='password']");
    const cancelBtnPassword = $(".user-profile-password .cancel-btn");

    if (cancelBtnPassword.length) {
        cancelBtnPassword.on("click", function (e) {
            e.preventDefault();
            passwordInputs.val("");
        });
    }
});
