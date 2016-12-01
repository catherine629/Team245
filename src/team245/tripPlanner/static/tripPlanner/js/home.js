function getimage(address_id,address_image_dom){
  $.get("/tripPlanner/get_address_image/"+address_id)
  .done(function(data){
    address_image_dom.attr("src",data);
  })
}


$(function(){
  var images=$(".img-trip")
  for(var i=0;i<images.length;i++){
    var address_dom=$(images[i]);
    var address_id=address_dom.siblings(".hidden").text();
    getimage(address_id,address_dom);
  }
})
