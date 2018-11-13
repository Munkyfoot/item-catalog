$(function () {
    $.ajax("/api/catalog").done(function(data){
        //$('#catalogOutput').text(JSON.stringify(data));
    });
});