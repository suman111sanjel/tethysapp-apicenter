$(function() {
  $(".nav-li").eq(2).addClass('active-nav-li');


  setTimeout(function(){

  var tokenImageWidth=$('#inner-app-content').width()-55;
  $('.registration-image-token').css('width',tokenImageWidth);

  }, 1500);
});


