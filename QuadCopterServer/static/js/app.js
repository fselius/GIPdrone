/** On load execution: * */

var map = null;
var drawInteraction = null;
var drawOverlay = null;
var autoUpdate = false;
var followDrone = false;
var lowBattery = 20;

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
		$("#battery").html(data.battery.toFixed(1));
	});
	updateBatteryTextColor();
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
	map = createMap();
	drawOverlay = createOverlay();
	drawOverlay.setMap(map);
	map.addInteraction(createModifyInteaction(drawOverlay));
	setInterval(updateDroneLocation, 300);
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

function createDrawInteraction(overlay, drawType) {
	return new ol.interaction.Draw({
		features : overlay.getFeatures(),
		/** @type {ol.geom.GeometryType} */
		type : drawType
	});
}

function onDrawOff(event) {
	if (drawInteraction == null) {
		return;
	}
	map.removeInteraction(drawInteraction);
	drawInteraction = null;
	return;
}

function onDrawPolygon(event) {
	onDrawOff(event);
	drawInteraction = createDrawInteraction(drawOverlay, "Polygon");
	map.addInteraction(drawInteraction);
}

function onDrawLineString(event) {
	onDrawOff(event);
	drawInteraction = createDrawInteraction(drawOverlay, "LineString");
	map.addInteraction(drawInteraction);
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
    $("#criticalBattery").val(lowBattery);
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
    lowBattery = parseFloat($("#criticalBattery").val());
    map.getView().setCenter(ol.proj.transform([formLat, formLon], 'EPSG:4326', 'EPSG:3857'));
    updateBatteryTextColor();
    $("#closeSettings").click();
}

function updateBatteryTextColor() {
    if ($("#battery").html() <= lowBattery) {
        $("#battery").css('color', 'red');
    }
    else {
        $("#battery").css('color', 'black');
    }
}
