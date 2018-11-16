$(function () {
    //Check to see if the user has altered the image url input.
    $('input[name=image_url]').change(function () {
        if ($('#item_image').length) {
            //If a preview image exists and the image url input is cleared, remove the preview.
            if ($(this).val().length == 0) {
                $('#item_image').remove();
            }
        }
        else {
            //Create image preview if none exists and set alt text in case of an error with the image url
            $(this).after("<img id='item_image' src='' alt='Invalid URL!'/>");
        }

        //Try and set image src to image url. Clear src on error.
        $('#item_image').on('error', function () {
            $(this).attr("src", "");
        }).attr("src", $('input[name=image_url]').val());
    });

    $('form').submit(function (e) {
        //On form submit check to see if user has attempted to enter an invalid image url and raise an alert if so.
        if ($('#item_image').length) {
            if ($('#item_image').attr('src').length == 0) {
                e.preventDefault();
                alert("You must use a valid image url!");
            }
        }
    });
});