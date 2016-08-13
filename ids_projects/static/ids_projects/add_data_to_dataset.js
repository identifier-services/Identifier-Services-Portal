(function(window, $, undefined) {

    // The following lifted from stack overflow post by sigurd
    // http://stackoverflow.com/a/6533544/1344499
    $(function () {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
    });

    // The following lifted from stack overflow post by sigurd
    // http://stackoverflow.com/a/6533544/1344499
    function getCookie(c_name)
    {
        if (document.cookie.length > 0)
        {
            c_start = document.cookie.indexOf(c_name + "=");
            if (c_start != -1)
            {
                c_start = c_start + c_name.length + 1;
                c_end = document.cookie.indexOf(";", c_start);
                if (c_end == -1) c_end = document.cookie.length;
                return unescape(document.cookie.substring(c_start,c_end));
            }
        }
        return "";
     }

    var add_data = function add_data() {

        var selected_data = $('input[name=data_select][checked=checked]');
        var url = window.location.href;

        var postdata={
            selected : selected.map(function(index, item) {return item.value;});
        }

        var redirect_url = url.replace('/select_data/','/');
        var url = url.replace('/select_data/','/add_data/');

        $.post(url, postdata)
        .then(function(response) {
            window.location.replace(redirect_url);
        });
    };

    $('#id_select_data_form').on('submit', function(e) {
        e.preventDefault();
        add_data();
    });

})(window, jQuery);
