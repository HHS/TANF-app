(function ($) {
    var filetypes = /\.(zip|exe|dmg|pdf|doc.*|xls.*|ppt.*|mp3|txt|rar|wma|mov|avi|wmv|flv|wav)$/i;
    var baseHref = '';
    if ($('base').attr('href') != undefined) baseHref = $('base').attr('href');
    var hrefRedirect = '';
    
    $('document').ready(function () {
        
        $('body').delegate('a', 'click', function(event) {
            var el = $(this);
            var href = (typeof(el.attr('href')) != 'undefined' ) ? el.attr('href') : '';
            var isThisDomain = href.match(document.domain.split('.').reverse()[1] + '.' + document.domain.split('.').reverse()[0]);
            var track = false;
            // track all clicks on files
            if (href.match(filetypes)) {
                track = true;
            }
            // don't track all clicks to .htm files, only ones in the attachments
            if (href.match(/\.(htm.*)$/i) && el.parents('.attachments-list').length) {
                track = true;
            }
            if (typeof ga !== 'function') {
                track = false;
            }
            if (!href.match(/^javascript:/i)) {
                if (track) {
                    parts = href.split('/sites/default/files/');
                    f = (parts.length==2) ? parts[1] : parts[0];
                    ga('send', 'event', 'File', 'Download', 'public://'+f);
                }
            }
        });
    });

})(jQuery);
;
