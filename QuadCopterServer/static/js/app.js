var isDrawable = false; 
var map;
var drawToggleElement = document.getElementById("drawToggle");
var checkpoints = [];

$(document).ready(init)

function init() {
	var satTileServer = "http://" + location.host + "/tiles/sat/{z}/{x}/{y}.jpg"
	var satLayer = new ol.layer.Tile({
	  source: new ol.source.XYZ( {urls: [satTileServer, satTileServer, satTileServer]})
	})
	var controls = new ol.Collection([mousePositionControl , new ol.control.FullScreen()])
	map = new ol.Map({
		  layers: [satLayer],
		  target: 'map',
		  controls:  controls,
		  view: new ol.View({
		    center: [3901957, 3838820],
		    zoom: 10
		  })
	});
}


/***********************/
var mousePositionControl = new ol.control.MousePosition({
  coordinateFormat: ol.coordinate.createStringXY(5),
  projection: 'EPSG:4326',
  // comment the following two lines to have the mouse position
  // be placed within the map.
  className: 'custom-mouse-position',
  //target: document.getElementById('mouse-position'),
  undefinedHTML: '&nbsp;'
});






// The features are not added to a regular vector layer/source,
// but to a feature overlay which holds a collection of features.
// This collection is passed to the modify and also the draw
// interaction, so that both can add or modify features.
function getOverlay() {
    var featureOverlay = new ol.FeatureOverlay({
      style: new ol.style.Style({
        fill: new ol.style.Fill({
          color: 'rgba(255, 255, 255, 0.15)'
        }),
        stroke: new ol.style.Stroke({
          color: '#ffcc33',
          width: 2
        }),
        image: new ol.style.Circle({
          radius: 5,
          fill: new ol.style.Fill({
            color: '#ffcc33'
          })
        })
      })
    });
    featureOverlay.setMap(map);
    return featureOverlay;
}

var modify = new ol.interaction.Modify({
  features: getOverlay().getFeatures(),
  // the SHIFT key must be pressed to delete vertices, so
  // that new vertices can be drawn at the same position
  // of existing vertices
  deleteCondition: function(event) {
    return ol.events.condition.shiftKeyOnly(event) &&
        ol.events.condition.singleClick(event);
  }
});
map.addInteraction(modify);



var draw; // global so we can remove it later
function addInteraction() {
  var a = getOverlay();
  draw = new ol.interaction.Draw({
    features: a.getFeatures(),
    type: /** @type {ol.geom.GeometryType} */ (typeSelect.value)
  });
  map.addInteraction(draw);
}

var onDrawToggle = function() {
	if (isDrawable) {
		isDrawable = false;
		map.removeInteraction(draw);
		drawToggleElement.textContent = "Turn map drawing on"
		return;
	}
	isDrawable = true;
	drawToggleElement.textContent = "Turn map drawing off";
	addInteraction();
}

function onDrawAdded(event) {

} 

var typeSelect = document.getElementById('typeSelector');


/**
 * Let user change the geometry type.
 * @param {Event} e Change event.
 */
/*typeSelect.onchange = function(e) {
  map.removeInteraction(draw);
  addInteraction();
};*/




