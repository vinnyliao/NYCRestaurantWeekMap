var map_id = 2695980;
var map;
var fusionTablesLayer;

$(document).ready(function() {

	$("select").change(function() {
		fusionTablesLayer.setQuery(
			"SELECT Address FROM " + map_id + " " +
			"WHERE Meals CONTAINS IGNORING CASE '" + $("#meal").val() + "' " +
			"AND Cuisine CONTAINS IGNORING CASE '" + $("#cuisine").val() + "' " +
			"AND Rating >= " + $("#min_rating").val() + " " +
			"AND Price CONTAINS IGNORING CASE '" + $("#min_price").val() + "' "
		);
		fusionTablesLayer.setMap(map);
	})

	$("input").change(function() {
		fusionTablesLayer.setQuery(
			"SELECT Address FROM " + map_id + " " +
			"WHERE Meals CONTAINS IGNORING CASE '" + $("#meal").val() + "' " +
			"AND Cuisine CONTAINS IGNORING CASE '" + $("#cuisine").val() + "' " +
			"AND Rating >= " + $("#min_rating").val() + " " +
			"AND Price CONTAINS IGNORING CASE '" + $("#min_price").val() + "' "
		);
		fusionTablesLayer.setMap(map);
	})

	$("div#accordion").accordion({
		autoHeight: false,
		collapsible: true,
		icons: {
			header: "ui-icon-circle-plus",
			headerSelected: "ui-icon-circle-minus"
		}
	});

	var latitude = 40.714353;
	var longitude = -74.005973;
	if (navigator.geolocation)
	{
		function successCallback(position) {
			latitude = position.coords.latitude;
			longitude = position.coords.longitude;
		}
		function errorCallback(error) {}
		navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
	}
	var latLng = new google.maps.LatLng(latitude, longitude);
	var mapOptions = {
		center: latLng,
		zoom: 12,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		mapTypeControl: false,
		panControl: false,
		rotateControl: false,
		streetViewControl: true,
		streetViewControlOptions: {
			position: google.maps.ControlPosition.RIGHT_TOP
		},
		zoomControl: false,
	};
	map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

	fusionTablesLayer = new google.maps.FusionTablesLayer(map_id);	
	fusionTablesLayer.setMap(map);



});