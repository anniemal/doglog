$(function() {


// Find the track_id of the workout they are viewing
	console.log(json_walks);

	// data = JSON.parse(json_walks);
	data = json_walks;
	
	latest_walk = data[data.length-1];
	console.log(latest_walk);

	tracking_data=latest_walk['walk_location'];
	console.log(tracking_data);
	tracking_data=JSON.parse(tracking_data);
	console.log(tracking_data);
	var lat_lng=[];
	for (var i=0;i<tracking_data.length;i++)
	{
		start_walk=tracking_data[i];
		lat=start_walk['ab'];
		lng=start_walk['$a'];

		myLatLng=new google.maps.LatLng(lng,lat);
		lat_lng.push(myLatLng);
	}
	var myOptions = {
	      zoom: 15,
	      center:lat_lng[0],
	      mapTypeId: google.maps.MapTypeId.ROADMAP
	    };
  
  	console.log(lat_lng[0]);
    //Create the Google Map, set options
   var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

   	var new_path = new google.maps.Polyline({
      path: lat_lng,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 2
   	});
   	new_path.setMap(map);

  });