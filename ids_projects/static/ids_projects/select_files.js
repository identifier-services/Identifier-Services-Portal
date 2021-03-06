(function(window, $, undefined) {
    function humanFileSize(bytes, si) {
        var thresh = si ? 1000 : 1024;
        if(Math.abs(bytes) < thresh) {
            return bytes + ' B';
        }
        var units = si
            ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
            : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
        var u = -1;
        do {
            bytes /= thresh;
            ++u;
        } while(Math.abs(bytes) >= thresh && u < units.length - 1);
        return bytes.toFixed(1)+' '+units[u];
    }

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

    var bind_chooser_events = function bind_chooser_events() {
        $('a.file').on('click', function(e) {
            e.preventDefault();
            var type = this.dataset.fileType;
            var path = this.dataset.filePath;
            if (type === 'dir') {
                $('#id_file_path').val(path);
                do_listing();
            }
        });

        $('button[name="file-open"]').on('click', function(e) {
            e.preventDefault();
            var path = this.dataset.filePath
            $('#id_file_path').val(path);
            do_listing();
        });

        $('button[name="file-select"]').on('click', function(e) {
            e.preventDefault();
            // TODO: make this a modal or something
            $("table").prepend("<div><h2 style='color: red'>Registering File...</h2></div>");
            var file_path = e.target['dataset']['filePath']
            select_file(file_path);
        });
    };

    var select_file = function select_file(file_path) {
        var url = window.location.href;

        var postdata={
            system_id : $('#id_system_id').val(),
            file_path : file_path
        }

//        var redirect_url = 'projects/';

//        if (url.indexOf("output") > -1) {
//            redirect_url = url.replace('file/select/output?process_uuid=','process/');
//        } else if (url.indexOf("input") > -1) {
//            redirect_url = url.replace('file/select/input?process_uuid=','process/');
//        } else if (url.indexOf("None") > -1) {
//            if (url.indexOf("specimen_uuid") > -1) {
//                redirect_url = url.replace('file/select/None?specimen_uuid=','specimen/');
//            } else if (url.indexOf("project_uuid") > -1) {
//                redirect_url = url.replace('file/select/None?process_uuid=','project/');
//            }
//        }

        if (postdata.system_id && postdata.file_path) {
            $.post(url, postdata)
//            .then(function(response) {
//                window.location.replace(redirect_url);
//            });
        }
    }

    var do_listing = function do_listing() {
        var system_id = $('#id_system_id').val();
        var file_path = $('#id_file_path').val();

        if (system_id && file_path) {
            $('#files_listing tbody').html(
                        '<tr><td colspan="4"><p class="alert">' +
                        '<i class="glyphicon glyphicon-refresh"></i> Loading files...' +
                        '</p></td></tr>');

            listing_uri = encodeURI('/dir/list/' + system_id + '/' + file_path)

            $.getJSON(listing_uri)

            .then(function(listing) {
                var file_rows = [];
                $.each(listing, function(i, file) {
                    var file_cols = [];
                    var icon = file.type === 'dir' ? 'folder-close' : 'file';
                    var date = new Date(file.lastModified);
                    file_cols.push('<td><a data-file-type="'+file.type+'" data-file-path="' + file.path + '" class="file" href="' + file.path + '"><i class="glyphicon glyphicon-' + icon + '"></i> ' + file.name + '</a></td>');
                    file_cols.push('<td>' + date.toLocaleString() + '</td>');
                    file_cols.push('<td>' + humanFileSize(file.length, true) + '</td>');

                    var actions = []
                    if (file.type === 'dir') {
                        actions.push('<button data-file-path="' + file.path + '" name="file-open" type="button" class="btn btn-sm btn-default">Open</button>')
                    }
                    actions.push('<button data-file-path="' + file.path + '" name="file-select" type="button" class="btn btn-sm btn-default">Select</button>')

                    file_cols.push('<td>' + actions.join('&nbsp;') + '</td>');
                    file_rows.push('<tr data-system-id="' + system_id + '" data-file-path="' + file.path + '">' + file_cols.join('') + '</tr>');
                });
                $('#files_listing tbody').html(file_rows.join(''));
                bind_chooser_events();
            })

            .fail(function(xhr){
                var err = JSON.parse(xhr.responseText);
                $('#files_listing tbody').html(
                    '<tr><td colspan="4"><p class="alert alert-danger">' +
                    err.message +
                    '</p></td></tr>');
            });
        }
    };

    $('#id_browse_system_form').on('submit', function(e) {
        e.preventDefault();
        do_listing();
    });

    $('#id_system_id, #id_file_path').on('change', do_listing);

})(window, jQuery);
