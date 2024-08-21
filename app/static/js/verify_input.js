$(document).ready(function() {
  const $inputs = $("input.verify-otp"),
        $button = $("#verifyButton"),
        $combinedOtp = $("#combinedOtp");

  function combineOtpValues() {
      const otpValue = $inputs.map(function() {
          return $(this).val();
      }).get().join('');
      $combinedOtp.val(otpValue);
  }

  function checkAllInputsFilled() {
      const allFilled = $inputs.toArray().every(input => $(input).val() !== '');
      if (allFilled) {
          $button.addClass("active");
      } else {
          $button.removeClass("active");
      }
  }

  function handleFocus(e) {
      const $input = $(e.target);
      if ($input.val().length > 0) {
          $input.select();
      }
  }

  function handleKeyup(e) {
      const $currentInput = $(e.target),
            $nextInput = $currentInput.next("input[type='number']"),
            $prevInput = $currentInput.prev("input[type='number']");

      if ($currentInput.val().length > 1) {
          $currentInput.val("");
          return;
      }

      if ($nextInput.length && $nextInput.is(":disabled") && $currentInput.val() !== "") {
          $nextInput.prop("disabled", false).focus();
      }

      if (e.key === "Backspace") {
          $inputs.each(function(index2, input) {
              if ($inputs.index($currentInput) <= index2 && $prevInput.length) {
                  $(input).prop("disabled", true).val("");
                  $prevInput.focus();
              }
          });
      }

      checkAllInputsFilled();
      combineOtpValues();

      if ($currentInput.is($inputs.last()) && $currentInput.val().length > 0) {
          $currentInput.select();
      }
  }

  $inputs.on("keyup", handleKeyup);
  $inputs.on("focus", handleFocus);

  $(window).on("load", function() {
      $inputs.first().focus();
  });

  $button.on("click", function() {
      combineOtpValues();
  });
});
