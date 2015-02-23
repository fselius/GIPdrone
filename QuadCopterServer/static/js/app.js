/** On load execution: * */

var map = null;
var drawInteraction = null;
var drawOverlay = null;
var autoUpdate = false;
var followDrone = false;
var registeredDrone = false;
var followIterator = 0;
var criticalBatteryLevel = 20;

/* Global placeholder for polygon/linestring coordinates */
var currentDrawLat = [];
var currentDrawLon = [];
var currentDrawType = "";


$(document).ready(init);

/** End of on load execution: * */

/** Functions * */

function getDroneFeature() {
	return map.getLayers().getArray()[1].getSource().getFeatures()[0];
}

function projectLatLong(lat, long) {
	return new ol.geom.Point(ol.proj.transform([ lat, long ], 'EPSG:4326',
			'EPSG:3857'));
}

function updateDroneLocation() {
	if (!autoUpdate) {
		return;
	}
	jQuery.getJSON("../flightData", function(data) {
		getDroneFeature().setGeometry(projectLatLong(data.lat, data.long));
		$("#lat").html(data.lat.toFixed(5));
		$("#long").html(data.long.toFixed(5));
		$("#height").html(data.height.toFixed(2));
		$("#orientation").html(data.orientation.toFixed(2));
		batteryLevel = data.battery.toFixed(1);
		$("#battery").html(batteryLevel);
		$("#battery").toggleClass("criticalLevel", batteryLevel <= criticalBatteryLevel);
	});
	if (followDrone) {
	    followIterator++;
	    followIterator = followIterator%5;
	    if (followIterator == 0) {
            var lat = parseFloat($("#lat").html());
            var lon = parseFloat($("#long").html());
            map.getView().setCenter(ol.proj.transform([lat, lon], 'EPSG:4326', 'EPSG:3857'));
	    }
	}
}

function toggleAutoUpdateFlightData() {
	autoUpdate = !autoUpdate;
	$(this).toggleClass("active", autoUpdate);
}

function init() {
	$("#autoUpdateFlightData").click(toggleAutoUpdateFlightData);
	$("#drawOff").click(onDrawOff);
	$("#drawPolygon").click(onDrawPolygon);
	$("#drawLineString").click(onDrawLineString);
	$("#settings").click(fillSettingsModal);
	$("#followToggle").click(onFollowToggle);
	$("#saveSettings").click(onSaveSettings);
	$("#sendDroneIp").click(sendDroneIp);
	$(window).resize(fixMapSize);
	map = createMap();
	drawOverlay = createOverlay();
	drawOverlay.setMap(map);
	map.addInteraction(createModifyInteaction(drawOverlay));
	setInterval(updateDroneLocation, 300);
	fixMapSize();
}

function createDroneLayer() {
	var iconFeature = new ol.Feature({
		geometry : projectLatLong(35.01574, 32.77849)
	});

	iconFeature.setStyle(new ol.style.Style({
		image : new ol.style.Icon(/** @type {olx.style.IconOptions} */
				({
					anchor : [ 0.9, 80 ],
					anchorXUnits : 'fraction',
					anchorYUnits : 'pixels',
					opacity : 0.75,
					src : 'images/drone.png'
				}))
			}));
	return new ol.layer.Vector({
		source : new ol.source.Vector({
			features : [ iconFeature ]
		})
	});
}

function createSatLayer() {
	var satTileServer = "http://" + location.host
			+ "/tiles/sat/{z}/{x}/{y}.jpg";
	return new ol.layer.Tile({
		source : new ol.source.XYZ({
			urls : [ satTileServer, satTileServer, satTileServer ]
		})
	});
}

function craeteMousePositionControl() {
	return new ol.control.MousePosition({
		coordinateFormat : ol.coordinate.createStringXY(5),
		// projection : 'EPSG:3857',
		projection : 'EPSG:4326',
		undefinedHTML : '&nbsp;',
		// Define this so position is not set by default css
		className : 'custom-mouse-position',
		// Choose specific element to attach to
		target : document.getElementById('mouse_location'),
	});
}

function createMap() {
	return new ol.Map({
		layers : [ createSatLayer(), createDroneLayer() ],
		target : 'map',
		controls : new ol.Collection([ craeteMousePositionControl() ]),
		view : new ol.View({
			center : [ 3898184, 3865621 ],
			zoom : 15
		})
	});
}

// The features are not added to a regular vector layer/source,
// but to a feature overlay which holds a collection of features.
// This collection is passed to the modify and also the draw
// interaction, so that both can add or modify features.
function createOverlay() {
	return new ol.FeatureOverlay({
		style : new ol.style.Style({
			fill : new ol.style.Fill({
				color : 'rgba(255, 255, 255, 0.15)'
			}),
			stroke : new ol.style.Stroke({
				color : '#ffcc33',
				width : 2
			}),
			image : new ol.style.Circle({
				radius : 5,
				fill : new ol.style.Fill({
					color : '#ffcc33'
				})
			})
		})
	});
}

function createModifyInteaction(overlay) {
	return new ol.interaction.Modify({
		features : overlay.getFeatures(),
		// the SHIFT key must be pressed to delete vertices, so
		// that new vertices can be drawn at the same position
		// of existing vertices
		deleteCondition : function(event) {
			return ol.events.condition.shiftKeyOnly(event)
					&& ol.events.condition.singleClick(event);
		}
	});
}

function createSelectInteraction(overlay) {
	return new ol.interaction.Select({
		features : overlay.getFeatures(),
		removeCondition : function(event) {
			return ol.events.condition.altKeyOnly(event)
			&& ol.events.condition.singleClick(event);
		}
	});
}

//Double click validator
function coordinatesExist(lat, lon) {
    var sameLat = currentDrawLat[currentDrawLat.length - 1] == lat;
    var sameLon = currentDrawLon[currentDrawLon.length - 1] == lon;
    return sameLat && sameLon;
}
function createDrawInteraction(overlay, drawType) {
	return new ol.interaction.Draw({
		features : overlay.getFeatures(),
		/** @type {ol.geom.GeometryType} */
		type : drawType
	});
}

function addDrawCoordinates(event) {
    var coor = map.getEventCoordinate(event);
    var lat = coor[0];
    var lon = coor[1];
    var coordinates = {"lat": lat, "lon": lon};
    if (coordinatesExist(lat, lon) == false) {
        //make sure we add a real point and not accidentally from a double click
        currentDrawLat.push(lat);
        currentDrawLon.push(lon);
    }
}

function finishDrawing() {
    alert ("Finished drawing track. Sending to drone");
    //ask the user if he wants to send this drawing as a path or it's just junk
    var points = [];
    for (i = 0; i < currentDrawLat.length; i++) {
        var point = {"lat":currentDrawLat[i], "lon":currentDrawLon[i]};
        points.push(point);
    }

    var trackData = { "drawType": currentDrawType, "drawCoordinates":points};
    //post request that track to the server
    currentDrawLat = [];
    currentDrawLon = [];

}

function onDrawOff(event) {
	if (drawInteraction == null) {
		return;
	}
	$(map).click(addDrawCoordinates()).off();
    $(map).dblclick(finishDrawing).off();
	map.removeInteraction(drawInteraction);
	drawInteraction = null;
    currentDrawType = "";
	return;
}

function onDrawPolygon(event) {
	onDrawOff(event);
    currentDrawType = "Polygon";
	drawInteraction = createDrawInteraction(drawOverlay, "Polygon");
	map.addInteraction(drawInteraction);
	$(map).click(addDrawCoordinates);
    $(map).dblclick(finishDrawing);
}

function onDrawLineString(event) {
	onDrawOff(event);
    currentDrawType = "LineString";
	drawInteraction = createDrawInteraction(drawOverlay, "LineString");
	map.addInteraction(drawInteraction);
    $(map).click(addDrawCoordinates);
    $(map).dblclick(finishDrawing);
}

function setFollowToggle() {
    if (followDrone) {
        $("#followToggle").attr("aria-pressed", "true");
        $("#followToggle").attr("tooltip", "Currently centering map on drone movement");
        $("#followToggle").text("On");
    }
    else {
        $("#followToggle").attr("aria-pressed", "false");
        $("#followToggle").attr("tooltip", "Currently not centering map on drone movement");
        $("#followToggle").text("Off");
    }
}

function fillSettingsModal(event) {
    $("#criticalBattery").val(criticalBatteryLevel);
    var center = ol.proj.transform(map.getView().getCenter(), 'EPSG:3857', 'EPSG:4326');
    $("#mapCenterLat").val(center[0]);
    $("#mapCenterLon").val(center[1]);
    setFollowToggle();
}

function onFollowToggle(event) {
    followDrone = !followDrone;
    setFollowToggle();
}

function onSaveSettings(event) {
    var formLat = parseFloat($("#mapCenterLat").val());
    var formLon = parseFloat($("#mapCenterLon").val());
    criticalBatteryLevel = parseFloat($("#criticalBattery").val());
    map.getView().setCenter(ol.proj.transform([formLat, formLon], 'EPSG:4326', 'EPSG:3857'));
    $("#closeSettings").click();
}

function fixMapSize() {
	//required so that size fix occurs after resize event is finished
	setTimeout(function() {
		h = $(window).height() - 90;
		w = $(window).width() - 270; 
		map.setSize([w, h]);
	}, 300);
}

function sendDroneIp() {
	$.get("../changeDrone?ip=" + $("#droneIp").val(), function(data) {
		if(data == "ok") {
			$("#flight_data").css("display","block");
			$("#registerDrone").css("display", "none");
            registeredDrone = true;
		}
	});
}
