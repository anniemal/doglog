$(function() {
var poop_events=[];
var pee_events=[];
var friend_events=[];
var frenemy_events=[];

var poop_image = '../static/img/poop.png';
var pee_image = '../static/img/pee.gif';
var friend_image = '../static/img/dog_happy.gif';
var frenemy_image='../static/img/dog_sad.gif';
var lat_lng=[];

// Find the track_id of the workout they are viewing
	console.log(json_walks);

	// data = JSON.parse(json_walks);
	data = json_walks;
	
	latest_walk = data[data.length-1];
	console.log(latest_walk);
	events=latest_walk['events'];
	events=JSON.parse(events);
	console.log(events);
	tracking_data=latest_walk['walk_location'];
	console.log(tracking_data);
	tracking_data=JSON.parse(tracking_data);
	console.log(tracking_data);
	console.log(pee_events);
	console.log(poop_events);

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
   	for (var i=0; i<events.length;i++)

	{
		event_one=events[i];
		if (event_one['pee']!=null)
		{
		pee_events.push(event_one['pee']);
		}
		else if (event_one['poop']!=null)
		{
		poop_events.push(event_one['poop']);
		}
		else if (event_one['friend']!=null)
		{
		friend_events.push(event_one['friend']);
		}
		else if (event_one['frenemy']!=null)
		{	
		frenemy_events.push(event_one['frenemy']);
		}
	}

	if (poop_events.length >0)
	{
	for (var i=0; i<poop_events.length;i++)
	{
	var type_location='poop_location'+i;
	var poop_marker= 'poop_marker'+i;
	console.log(type_location);
  	type_location = new google.maps.LatLng(poop_events[i][0], poop_events[i][1]);
  	var poop_marker = new google.maps.Marker({
    	position: type_location,
    	map: map,
    	icon: poop_image
		});
	}
	}
	if (pee_events.length>0)
	{
	for (var i=0; i<pee_events.length;i++)
	{
	var type_location='pee_location'+i;
	var pee_marker= 'pee_marker'+i;
	console.log(type_location);
  	type_location = new google.maps.LatLng(pee_events[i][0], pee_events[i][1]);
  	var pee_marker = new google.maps.Marker({
    	position: type_location,
    	map: map,
    	icon: pee_image
		});
	}
	}
	if (friend_events.length>0)
	{	
	for (var i=0; i<friend_events.length;i++)
	{
	var type_location='friend_location'+i;
	var friend_marker='friend_marker'+i;
	console.log(type_location);
  	type_location = new google.maps.LatLng(friend_events[i][0], friend_events[i][1]);
  	var friend_marker = new google.maps.Marker({
    	position: type_location,
    	map: map,
    	icon: friend_image
		});
	}
	}
	if (frenemy_events.length>0)
	{
	for (var i=0; i<frenemy_events.length;i++)
	{
	var type_location='frenemy_location'+i;
	var frenemy_marker='frenemy_marker'+i;
	console.log(type_location);
  	type_location = new google.maps.LatLng(frenemy_events[i][0], frenemy_events[i][1]);
  	var frenemy_marker = new google.maps.Marker({
    	position: type_location,
    	map: map,
    	icon: frenemy_image
		});
	}
	}

   	var new_path = new google.maps.Polyline({
      path: lat_lng,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 2
   	});

   	new_path.setMap(map);
  });