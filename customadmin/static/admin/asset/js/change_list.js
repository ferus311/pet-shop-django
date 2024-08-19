$(document).ready(function() {
  // Lấy tất cả các checkbox
  const $checkboxes = $('input[name="_selected_action"]');
  // Lấy phần tử hiển thị số lượng mục đã chọn
  const $selectedCountElement = $('#selected-count');

  // Hàm cập nhật số lượng mục đã chọn
  function updateSelectedCount() {
    const selectedCount = $checkboxes.filter(':checked').length;
    $selectedCountElement.text(selectedCount);
  }

  // Thêm sự kiện thay đổi cho tất cả các checkbox
  $checkboxes.on('change', updateSelectedCount);

  // Cập nhật số lượng mục đã chọn khi trang được tải
  updateSelectedCount();
});
