function initialize() {
  var maps = document.getElementsByClassName("map");
  for(var i = 0; i < maps.length; i++){
    var directionsService = new google.maps.DirectionsService;
    var directionsDisplay = new google.maps.DirectionsRenderer;

    var dayTripId = maps[i].id;
    var path = maps[i].value;
    var mapId = "map-" + dayTripId;

    var map = new google.maps.Map(document.getElementById(mapId), {
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    if(!path.includes("|")) {
      if(path.length == 0) {
        var latlng = document.getElementById("trip-location").value.split(",");
        var location = {};
        location["lat"] = parseFloat(latlng[0]);
        location["lng"] = parseFloat(latlng[1]);

        var marker = new google.maps.Marker({
          position: location,
          map: map
        });

        map.setZoom(10);
        map.setCenter(marker.getPosition());

        var routeLocations = '<input type="hidden" name="route-' + dayTripId + '" value="#">';
        var daytrips = document.getElementById("dayTrips");
        dayTrips.innerHTML += routeLocations;
      } else {
        var latlng = path.split(",");
        var location = {};
        location["lat"] = parseFloat(latlng[0]);
        location["lng"] = parseFloat(latlng[1]);

        // console.log(location);
        var marker = new google.maps.Marker({
          position: location,
          map: map
        });

        var bounds = new google.maps.LatLngBounds();
        bounds.extend(marker.position);
        map.fitBounds(bounds);

        var oldRouteId = "oldRoute-" + dayTripId;
        var oldRoute = document.getElementById(oldRouteId).value;
        var routeLocations = '<input type="hidden" name="route-' + dayTripId + '" value="' + oldRoute + '">';
        var daytrips = document.getElementById("dayTrips");
        dayTrips.innerHTML += routeLocations;
        // console.log(dayTrips.innerHTML);

        var panelId = "panel-" + dayTripId;
        var unitId = "unitid-" + oldRoute;
        var summaryPanel = document.getElementById(panelId);
        var attractionName = document.getElementById(unitId).value;

        // console.log(attractionName);

        summaryPanel.innerHTML = '';
        summaryPanel.innerHTML += '<div class="row leftalign">' + attractionName + '</div>';
        summaryPanel.innerHTML += '<div class="row leftalign">' + 0.000 + 'km</div>';
      }
    } else {
      directionsDisplay.setMap(map);
      calculateAndDisplayRoute(directionsService, directionsDisplay, path, dayTripId);
    }
  }
  // console.log(document.getElementById("dayTrips").innerHTML);
}

function calculateAndDisplayRoute(directionsService, directionsDisplay, path, dayTripId) {
  // console.log(path);
  var locations = path.split("|");
  if (locations.length == 2) {
    directionsService.route({
      origin: locations[0],
      destination: locations[1],
      travelMode: google.maps.TravelMode.DRIVING
    }, function(response, status) {
      if (status === google.maps.DirectionsStatus.OK) {
        directionsDisplay.setDirections(response);
        displaySummary(response, dayTripId);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
  } else {
    var waypts = [];
    for(var i = 1; i < locations.length - 1; i++) {
      waypts.push({
        location: locations[i],
        stopover: true
      });
    }
    // console.log(waypts);

    directionsService.route({
      origin: locations[0],
      destination: locations[locations.length - 1],
      waypoints: waypts,
      optimizeWaypoints: true,
      travelMode: google.maps.TravelMode.DRIVING
    }, function(response, status) {
      if (status === google.maps.DirectionsStatus.OK) {
        // console.log("success");
        directionsDisplay.setDirections(response);
        displaySummary(response, dayTripId);
      } else {
        // console.log("fail");
        window.alert('Directions request failed due to ' + status);
      }
    });
  }
}

function displaySummary(response, dayTripId) {
  var route = response.routes[0];
  var waypntOrder = route.waypoint_order;
  var panelId = "panel-" + dayTripId;
  var oldRouteId = "oldRoute-" + dayTripId;
  // console.log(waypntOrder);

  var summaryPanel = document.getElementById(panelId);
  var oldRoute = document.getElementById(oldRouteId).value;
  var oldPoints = oldRoute.split("|");
  // console.log(oldPoints);
  // console.log(waypntOrder);

  var totalDist = 0;
  var j = 0;
  summaryPanel.innerHTML = '';
  console.log(route.legs.length);

  if(route.legs.length == 1) {
    unitId = "unitid-" + oldPoints[0];
    startAttraction = document.getElementById(unitId).value;

    unitId = "unitid-" + oldPoints[1];
    endAttraction = document.getElementById(unitId).value;

    summaryPanel.innerHTML += '';
    summaryPanel.innerHTML += '<div class="row leftalign"><strong>FROM: '+ startAttraction +'</strong> ' + route.legs[0].start_address + '</div>';
    summaryPanel.innerHTML += '<div class="row leftalign"><strong>TO: ' + endAttraction + '</strong> ' + route.legs[0].end_address + '</div>';
    summaryPanel.innerHTML += '<div class="row leftalign"><strong>DISTANCE: </strong>' + (parseInt(route.legs[0].distance.value)/1000).toFixed(3) + 'km</div>';
    totalDist += parseInt(route.legs[0].distance.value);
    summaryPanel.innerHTML += '<div class="row leftalign"><strong>TOTAL DISTANCE: </strong>' + (totalDist/1000).toFixed(3) + 'km</div>';
  } else {
    for (var i = 0; i < route.legs.length; i++) {
      var routeSegment = i + 1;
      var startAttraction = "";
      var endAttraction = "";
      var unitId = "";
      var sequence = 0;

      if (i == 0) {
        unitId = "unitid-" + oldPoints[0];
        startAttraction = document.getElementById(unitId).value;

        sequence = waypntOrder[0] + 1;
        unitId = "unitid-" + oldPoints[sequence];
        endAttraction = document.getElementById(unitId).value;
      } else if (i == route.legs.length - 1) {
        sequence = waypntOrder[waypntOrder.length - 1] + 1;
        unitId = "unitid-" + oldPoints[sequence];
        startAttraction = document.getElementById(unitId).value;

        unitId = "unitid-" + oldPoints[oldPoints.length - 1];
        endAttraction = document.getElementById(unitId).value;
      } else {
        sequence = waypntOrder[j++] + 1;
        unitId = "unitid-" + oldPoints[sequence];
        startAttraction = document.getElementById(unitId).value;

        sequence = waypntOrder[j] + 1;
        unitId = "unitid-" + oldPoints[sequence];
        endAttraction = document.getElementById(unitId).value;
      }

      // summaryPanel.innerHTML += '<div class="row leftalign"><strong>Route Segment: ' + routeSegment + '</strong></div>';
      summaryPanel.innerHTML += '';
      summaryPanel.innerHTML += '<div class="row leftalign"><strong>FROM: '+ startAttraction +'</strong> ' + route.legs[i].start_address + '</div>';
      summaryPanel.innerHTML += '<div class="row leftalign"><strong>TO: ' + endAttraction + '</strong> ' + route.legs[i].end_address + '</div>';
      summaryPanel.innerHTML += '<div class="row leftalign"><strong>DISTANCE: </strong>' + (parseInt(route.legs[i].distance.value)/1000).toFixed(3) + 'km</div>';
      totalDist += parseInt(route.legs[i].distance.value);
    }
    summaryPanel.innerHTML += '<div class="row leftalign"><strong>TOTAL DISTANCE: </strong>' + (totalDist/1000).toFixed(3) + 'km</div>';
  }
  var routeLocations = '<input type="hidden" name="route-' + dayTripId + '" value="';
  var newRoute = oldPoints[0] + "|";
  for (var i = 0; i < waypntOrder.length; i++) {
    var sequence = waypntOrder[i] + 1;
    newRoute += oldPoints[sequence] + "|";
  }
  newRoute += oldPoints[oldPoints.length - 1];
  routeLocations += newRoute + '">';
  console.log(panelId);
  console.log(summaryPanel.innerHTML);

  var daytrips = document.getElementById("dayTrips");
  dayTrips.innerHTML += routeLocations;
}
