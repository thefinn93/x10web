var API = "/api/action";

$(".action").on('click', function(e) {
  target = $(e.currentTarget);
  target.addClass("disabled");
  var data = {
    housecode: target.data('housecode'),
    unit: target.data('unit'),
    action: target.data('action'),
    token: getToken()
  };
  $.post(API, data, function(token) {
    target.removeClass("disabled");
  });
});
