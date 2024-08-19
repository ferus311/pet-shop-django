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
