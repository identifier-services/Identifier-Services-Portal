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

    var foo_bar = function foo_bar() {

        var selected_data = $('input[name=request_doi][checked=checked]');
        var url = window.location.href;
        var selected = selected_data.map(function(index, item) {return item.value;})

        var postdata={
            selected : selected
        }

        var redirect_url = url.replace('/request_doi/','/');
        var url = url.replace('/request_doi/','/request_doi2/');

        console.log(url)
        console.log(redirect_url)
        console.log(postdata)

        $.post(url, postdata)
        .then(function(response) {
            window.location.replace(redirect_url);
        });
    };

    $('#id_request_doi_form').on('submit', function(e) {
        e.preventDefault();
        foo_bar();
    });

})(window, jQuery);
