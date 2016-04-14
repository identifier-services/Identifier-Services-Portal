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

    var get_fields = function get_fields() {
        var url = window.location.pathname;

        var postdata={
            process_type : $('#id_process_type').val(),
            type_selected : 1
        }

        if (postdata.process_type) {
            $.post(url, postdata);
            // window.location.replace(url);
        }

    }

    $('#id_process_type').on('change', get_fields);

})(window, jQuery);
