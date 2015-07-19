$(".action").on('click', function(e) {
  target = $(e.currentTarget);
  target.addClass("disabled");
  var url = "/api/";
  url += target.data('housecode') + "/";
  url += target.data('unit') + "/";
  url += target.data('action');
  $.get(url, function() {
    target.removeClass("disabled");
  });
});
