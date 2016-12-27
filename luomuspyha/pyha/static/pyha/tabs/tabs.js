$(document).ready(function () {
    //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip({trigger: 'manual'}).tooltip('show');

    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {
 

        var $target = $(e.target);
    
        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(document).on('click',".next-step",function (e) {
        var $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(document).on('click',".prev-step",function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        prevTab($active);

    });
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

window.onload = function () {
    var reason = document.getElementById("reason");
        var func = function() { 
            if (reason.value !== '') {
              document.getElementById("to_step_3").disabled = false;      
              
            } else {
              document.getElementById("to_step_3").disabled = true;         
              var $tabs = $('.wizard .nav-tabs li')
              var $summary_tab = $tabs[$tabs.length - 1]
              $summary_tab.className = 'disabled'
            }
        }
      reason.onkeyup = func;
      reason.onchange = func;
}

$(window).on('resize', function () {
  $('.nav-tabs > li a[title]').tooltip('show')
})
