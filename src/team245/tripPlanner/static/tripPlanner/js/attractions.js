function getimage(attraction_id,image_dom){
  $.get("/tripPlanner/get_image/"+attraction_id)
  .done(function(data){
    image_dom.attr("src",data);
  })
}

$(function(){
  $("body").on('hidden.bs.modal','.modal',function(){
    $('.detail-title').empty();
    $('.detail-body').empty();
  });
  var images=$(".thumbnail")
  for(var i=0;i<images.length;i++){
    var image=$(images[i]);
    var attraction_dom=image.children("img");
    var attraction_id=image.children(".hidden_attraction_id").text();
    getimage(attraction_id,attraction_dom);
  }
})

var attraction_name=""
var attraction_id=""
//function for add trip to right column
$(".attractions").on('click','.add_day',function(e){
  console.log("here")
  attraction_name=$(e.target).parent().siblings(".hidden_attraction_name").text();
  console.log(attraction_name)
  attraction_id=$(e.target).parent().siblings(".hidden_attraction_id").text();
  console.log(attraction_id)
  $('#myModal').modal({show:true});
});

$(".attractions").on('click','.show_detail',function(e){
  attraction_name=$(e.target).parent().siblings(".hidden_attraction_name").text();
  attraction_id=$(e.target).parent().siblings(".hidden_attraction_id").text();
  $.get('/tripPlanner/getAttractionDetail/'+attraction_id)
  .done(function(data){
    json=JSON.parse(data);
    $('.detail-title').text(json['name']);
    $('.detail-body').append(json['html']);
    $('#detailModal').modal({show:true});
  });
});



$("#myModal").on('click','li',function(e){
  var day=$(e.target).attr("id")
  var day_id="day_"+day+"_ul";
  var daytrip_id=$('#day_'+day).children('p').text();
  var input_name= "daytrip_"+daytrip_id
  var ul=$('#'+day_id);
  ul.append("<li>"+attraction_name+"<div class='glyphicon glyphicon-chevron-down down'></div><div class='glyphicon glyphicon-chevron-up up'></div><div class='glyphicon glyphicon-minus delete'></div></li>");
  query = 'input[name='+input_name+']';
  var units = $(query).val() + "," + attraction_id;
  $(query).val(units);
  $('#myModal').modal('hide');
});


$("#page_roller").on('click','li',function(e){
  //change active page
  var li=$(e.target).parent();
  $("li[class='active']").attr("class","");
  li.attr("class","active");
  //remove content for attractions
  var attractions_div=$(".attractions")
  attractions_div.empty();
  //ajax call to retrieve new data
  var href=$(e.target).attr('href');
  $.get(href)
  .done(function(data){
    data=JSON.parse(data);
    attractions=data["attractions"]
    for(var i=0;i<attractions.length;i++){
      attractions_div.append(attractions[i].html);
    }
  });
  return false;
});


$(document).on('click', '.up', function() {
    var li = $(this).closest('li');
    li.prev('li').before(li);
});

$(document).on('click', '.down', function() {
  var li = $(this).closest('li');
  li.next('li').after(li);
});

$(document).on('click', '.delete', function() {
  $(this).parent().remove();
});
