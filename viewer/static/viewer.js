$(function() {
  $('.day.on').click(function(e) {
    var date = e.target.getAttribute('d');
    var kvs = data[date];
    var keys = [];
    for (var k in kvs) { keys.push(k); }
    keys.sort();

    var html = '';
    $.each(keys, function(i, maker) {
      html += '<div><b>' + maker + '</b>: ' + kvs[maker]['summary'] + '</div>\n';
    });

    var max_x = $(document.body).width() - $('#summary').width();

    $('#summary')
      .html(html)
      .show()
      .css({
        left: Math.min(e.pageX, max_x) + 'px',
        top: e.pageY + 'px'
      });
  });

  $('#summary').click(function() {
    $('#summary').hide();
  });
});
