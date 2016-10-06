(function(window, $, undefined) {

	
	// The following lifted from stack overflow post by sigurd
    // http://stackoverflow.com/a/6533544/1344499
    $(function () {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });

        // hide upload button
	    $("#id_upload_tips").hide();
	    $("#id_upload_dialog").hide();
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

     function display_file_upload() {     	
     	if ($("#id_upload_option").val() == 'Single') {
     		$("#id_upload_tips").hide();
     		$("#id_upload_dialog").hide();
     	}
     	else {
     		$("#id_upload_tips").show();
     		$("#id_upload_dialog").show();
     	}
     }

     $('#id_upload_option').on('change', display_file_upload);
     console.log("in the js function");

})(window, jQuery);