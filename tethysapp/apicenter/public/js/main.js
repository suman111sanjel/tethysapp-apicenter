$(function() {
    // $(".nav-li").on('click',function () {
    //     var indexG=$(this).index();
    //     var that=$(this);
    //     $(".nav-li").removeClass('active-nav-li');
    //     $(".nav-li").eq(indexG).addClass('active-nav-li');
    // });
    $('#app-content').append( $('#inner-app-content'));
    var ReqHeight=$( window ).height()-70;
    $('#inner-app-content').css("height", ReqHeight);
    $('#app-content-wrapper #app-content #app-navigation .nav li a ').css("color", '#75787b');



});

