function get_events(events, poop_events, pee_events, friend_events, frenemy_events) {
    for (var i = 0; i < events.length; i++) {
        event_one = events[i];
        if (event_one['pee'] != null) {
            pee_events.push(event_one['pee']);
        } else if (event_one['poop'] != null) {
            poop_events.push(event_one['poop']);
        } else if (event_one['friend'] != null) {
            friend_events.push(event_one['friend']);
        } else if (event_one['frenemy'] != null) {
            frenemy_events.push(event_one['frenemy']);
        }
    }
}

function make_marker(event_type, event_icon, map) {
    if (event_type.length > 0) {
        for (var i = 0; i < event_type.length; i++) {
            var type_location = event_type + i;
            var marker = event_type + i;
            console.log(type_location);
            type_location = new google.maps.LatLng(event_type[i][0], event_type[i][1]);
            marker = new google.maps.Marker({
                position: type_location,
                map: map,
                icon: event_icon
            });
        }
    }
}

function make_path(tracking_data, lat_lng) {
    for (var i = 0; i < tracking_data.length; i++) {
        start_walk = tracking_data[i];
        lat = start_walk['Ya'];
        lng = start_walk['Za'];
        // myLatLng = new google.maps.LatLng(lng, lat);
        myLatLng = new google.maps.LatLng(lat, lng);
        lat_lng.push(myLatLng);
    }
    var new_path = new google.maps.Polyline({
        path: lat_lng,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 2
    });
    return new_path;
}

function make_map(tracking_data) {
    var poop_events = [];
    var pee_events = [];
    var friend_events = [];
    var frenemy_events = [];
    var poop_image = '../static/img/poop.png';
    var pee_image = '../static/img/pee.gif';
    var friend_image = '../static/img/dog_happy.gif';
    var frenemy_image = '../static/img/dog_sad.gif';
    var lat_lng = [];
    new_path = make_path(tracking_data, lat_lng);

    var myOptions = {
        zoom: 15,
        center: lat_lng[0],
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    get_events(events, poop_events, pee_events, friend_events, frenemy_events);
    make_marker(poop_events, poop_image, map);
    make_marker(pee_events, pee_image, map);
    make_marker(friend_events, friend_image, map);
    make_marker(frenemy_events, frenemy_image, map);
    new_path.setMap(map);
}

$(function () {
    data = json_walks;
    events = data['events'];
    events = JSON.parse(events);
    tracking_data = data['walk_location'];
    tracking_data = JSON.parse(tracking_data);
    make_map(tracking_data);

});