(function ($, window) {
    var escape = $.url.escape;

    function slugPreview(options) {
        options = $.extend(true, slugPreview.defaults, options || {});

        var collected = this.map(function () {
            var element = $(this);
            var field = element.find('input');
            var preview = $(options.template);
            var value = preview.find('.slug-preview-value');
            var required = $('<div>').append($('.control-required', element).clone()).html();

            // Check if slugPreview already exists in the parent container
            if (element.parent().find('.slug-preview').length > 0) {
                return;
            }

            function setValue() {
                var val = escape(field.val()) || options.placeholder;
                value.text(val);
            }

            preview.find('strong').html(required + ' ' + options.i18n['URL'] + ':');
            preview.find('.slug-preview-prefix').text(options.prefix);
            preview.find('button').text(options.i18n['Edit']).click(function (event) {
                event.preventDefault();
                element.show();
                preview.hide();
            });

            setValue();
            field.on('change', setValue);

            element.after(preview).hide();

            return preview[0];
        });

        // Append the new elements to the current jQuery stack so that the caller
        // can modify the elements. Then restore the originals by calling .end().
        return this.pushStack(collected);
    }

    slugPreview.defaults = {
        prefix: '',
        placeholder: '',
        i18n: {
            'URL': 'URL',
            'Edit': 'Edit'
        },
        template: [
            '<div class="slug-preview">',
            '<strong></strong>',
            '<span class="slug-preview-prefix"></span><span class="slug-preview-value"></span>',
            '<button class="btn btn-default btn-xs"></button>',
            '</div>'
        ].join('\n')
    };

    $.fn.slugPreview = slugPreview;

    // Add CSRF token to AJAX requests
    $(document).ajaxSend(function(event, xhr, settings) {
        var csrf_value = $('meta[name=_csrf_token]').attr('content');
        if (!settings.crossDomain) {
            xhr.setRequestHeader('X-CSRFToken', csrf_value);
        }
    });

})(this.jQuery, this);