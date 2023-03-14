(function(w,d,$){
  $(d).ready(function(){

    let loadForm = function() {
      let btn = $(this);
      $.ajax({
        url: btn.attr("href"),
        type: 'get',
        dataType: 'json',
        beforeSend: function () {
          $("#contactModal").modal("show");
        },
        success: function (data) {
          $("#contactModal .modal-content").html(data.html_form);
        }
      });
      return false;
    };

    let saveForm = function() {
        let form = $('#contact-form');
        let btn = $("#submit-btn");
        $.ajax({
            url: '/blog/contact_us/',
            data: form.serialize(),
            type: 'post',
            dataType: 'json',
            beforeSend: function() {
                btn.prop('disabled', true);
            },
            success: function(data) {
              if (data.form_is_valid) {
                $("#contactModal .modal-content").html("<p>Thank you for your message!</p>");
                setTimeout(function() {
                  $("#contactModal").modal("hide");
                }, 2000);
              } else {
                $("#contactModal .modal-content").html(data.html_form);
              }
            },
        });
        return false;
    };


    $("body").on('click', '.js-load-form', loadForm);
    $("body").on('click', "#submit-btn", saveForm);
  })
})(window,document,jQuery);
