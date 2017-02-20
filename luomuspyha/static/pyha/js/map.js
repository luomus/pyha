var map;
var ajaxRequest;
var plotlist;
var plotlayers=[];

function initializeMap() {
	// set up the map
	map = new L.Map('filtermap');

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 0, maxZoom: 14, attribution: osmAttrib});		

	map.setView(new L.LatLng(62.14, 25.44),40);
	map.addLayer(osm);
}