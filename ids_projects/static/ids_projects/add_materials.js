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
        var url = window.location.href;

        var postdata={
            material_type : $('#id_material_type').val(),
            project_uuid : $('#id_project_uuid').val()
        }

        if (postdata.material_type) {
            $.post(url, postdata)
            .then(function(response) {
                $('#id_form_material_fields').html(response);
                $('#id_material_type').attr('disabled', true);
                $('#id_material_type').attr('readonly', true);
            });
        }
    }

    $('#id_material_type').on('change', get_fields);

})(window, jQuery);
