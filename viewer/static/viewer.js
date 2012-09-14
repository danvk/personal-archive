$(function() {
  $('.day.on').click(function(e) {
    e.preventDefault();
    e.stopPropagation();
    var date = e.target.getAttribute('d');
    $.ajax({
        type: 'POST',
        url: '/get_summary',
        dataType: 'json',
        data: { day: date } })
      .done(function(kvs) {
        var keys = [];
        for (var k in kvs) { keys.push(k); }
        keys.sort();

        var html = '';
        $.each(keys, function(i, maker) {
          html += '<div><b>' + maker + '</b>: ' +
              kvs[maker]['summary'].replace(/\n/g, '<br/>') + '</div>\n';
        });
        html += '<a href="/day/' + date.replace(/-/g, '/') + '">More</a>';

        var max_x = $(document.body).width() - $('#summary').width();

        $('#summary')
          .html(html)
          .show()
          .css({
            left: Math.min(e.pageX, max_x) + 'px',
            top: e.pageY + 'px'
          });

        $(window).on('click', function() {
          $('#summary').hide();
        });
    });
  });

  $('#summary').click(function() {
    $('#summary').hide();
  });
});
