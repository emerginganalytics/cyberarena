(function ($) {

    var body = $('body');
    var container = $('<div id="zz_frame"></div>');
    var frame = $('<div id="zz_media"></div>');
    var close_btn = $('<button class="zz_close">&times;</button>');
    var button_zoom = $('<div class="zz_controls"><button type="button" class="zz_zoom-in">Zoom In</button><button type="button" class="zz_zoom-out">Zoom Out</button></div>');
    var media = $('<img src="" />');

    $('.zz_image').click( function(e) {
        e.preventDefault();

        uri = $(this).attr('src');

        media.attr('src', uri);

        frame.append(media);
        container.append(frame);
        container.append(close_btn);
        container.append(button_zoom);

        body.append(container);

    });

    $('body').on('click', '.zz_zoom-in', function(e) {
        var myImg = $('#zz_media img');
        img = myImg.get(0);
        if(img !== 'undefined') {
            nW = parseInt(img.naturalWidth);

            zLW = nW * 2;

            offS = myImg.offset();
            t = offS.top;
            l = offS.left;

            var cW = myImg.innerWidth();

            if(cW >= zLW){
                alert("Maximum zoom-in level reached.");
            } else{
                myImg.innerWidth((cW + 50) + "px");
                if(offS.top > 25) {
                    t = offS.top - 25;
                }
                if(offS.left > 25) {
                    l = offS.left - 25;
                }
                myImg.offset({ top: t, left: l });
            }
        }
    })

    $('body').on('click', '.zz_zoom-out', function(e) {
        var myImg = $('#zz_media img');
        mediaOffS = $('#zz_media').offset();
        img = myImg.get(0);
        if(img !== 'undefined') {
            nW = parseInt(img.naturalWidth);

            zLW = nW / 2;

            offS = myImg.offset();
            t = offS.top;
            l = offS.left;

            var cW = myImg.innerWidth();

            if(cW <= zLW){
                alert("Maximum zoom-out level reached.");
            } else{
                myImg.innerWidth((cW - 50) + "px");
                if(offS.top < mediaOffS.top) {
                    t = offS.top + 25;
                }
                if(offS.left < mediaOffS.left) {
                    l = offS.left + 25;
                }
                myImg.offset({ top: t, left: l });
            }
        }
    })

    $('body').on('click', '.zz_close', function(e) {
        $('#zz_frame').remove();
    })

})(jQuery);