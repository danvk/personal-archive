$(function() {
  $(makers).each(function(i, maker) {
    $('<input type=checkbox />')
      .attr('id', 'chk' + i)
      .attr('maker', maker)
      .attr('checked', 'checked')
      .appendTo($('#checks'));
    $(' <label/>')
      .attr('for', 'chk' + i)
      .text(maker)
      .appendTo($('#checks'));
  });

  // returns an object whose keys are checked makers.
  var collect_checked_makers = function() {
    var checked = {};
    $('input[type=checkbox]').each(function() {
      if ($(this).prop('checked')) {
        checked[$(this).attr('maker')] = 1;
      }
    });
    return checked;
  };

  var pad = function(x) {
    return (x < 10 ? '0' : '') + x;
  };

  // Update on/off classes to reflect the checkboxes.
  var update_classes = function() {
    var makers = collect_checked_makers();
    $('.year').each(function(idx, div) {
      var $year = $(div);
      var y = parseInt($('b', $year).text(), 10);
      var m = 0, d = 0;
      $('div', $year).each(function(idx, div) {
        if ($(div).hasClass('first')) {
          m += 1;
          d = 1;
        } else {
          d += 1;
        }

        var day_str = '' + y + '-' + pad(m) + '-' + pad(d);
        var day_makers = day_to_makers[day_str];
        var on = false;
        if (day_makers) {
          for (var i = 0; i < day_makers.length; i++) {
            if (day_makers[i] in makers) {
              on = true;
              break;
            }
          }
        }

        $(div).removeClass('on off').addClass(on ? 'on' : 'off');
      });
    });
  };

  $('input[type=checkbox]').click(function(e) {
    update_classes();
  });

  $('#btnNone').click(function() {
    $('input[type=checkbox]').prop('checked', '');
    update_classes();
  });

  $('#btnAll').click(function() {
    $('input[type=checkbox]').prop('checked', 'checked');
    update_classes();
  });
});
