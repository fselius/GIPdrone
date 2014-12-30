/** On load execution: **/

var map = null;
var drawInteraction = null;
var drawOverlay = null;

$(document).ready(init)

/** End of on load execution: **/

/** Functions **/

function hideMouse() {
	$("#mouse_location").toggle();
}

function init() {
	$("#flightPlan").click(hideMouse);
	$("#drawOff").click(onDrawOff);
	$("#drawPolygon").click(onDrawPolygon);
	$("#drawLineString").click(onDrawLineString);
	map = createMap();
	drawOverlay = createOverlay();
	drawOverlay.setMap(map);
	map.addInteraction(createModifyInteaction(drawOverlay));
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
//		projection : 'EPSG:3857',
		projection : 'EPSG:4326',
		undefinedHTML : '&nbsp;',
		// Define this so position is not set by default css
		className : 'custom-mouse-position',
	// Choose specific element to attach to
		target: document.getElementById('mouse_location'),
	});
}

function createMap() {
	return new ol.Map({
		layers : [ createSatLayer() ],
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
