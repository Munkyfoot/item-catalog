$(function () {
    $('input[name=image_url]').change(function () {

        if ($('#item_image').length) {
            if ($(this).val().length == 0) {
                $('#item_image').remove();
            }
        }
        else {
            $(this).after("<img id='item_image' src='' alt='Invalid URL!'/>");
        }

        $('#item_image').on('error', function () {
            $(this).attr("src", "");
        }).attr("src", $('input[name=image_url]').val());
    });

    $('form').submit(function (e) {
        if ($('#item_image').length) {
            if ($('#item_image').attr('src').length == 0) {
                e.preventDefault();
                alert("You must use a valid image url!");
            }
        }
    });
});