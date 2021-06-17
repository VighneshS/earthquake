var urlParams = new URLSearchParams(window.location.search);
var page = urlParams.has('page') ? urlParams.get('page') : 1
var minMag = urlParams.has('minMag') ? urlParams.get('minMag') : -1
var maxMag = urlParams.has('maxMag') ? urlParams.get('maxMag') : 6
var lat = urlParams.has('lat') ? urlParams.get('lat') : null
var lon = urlParams.has('lon') ? urlParams.get('lon') : null
var dist = urlParams.has('dist') ? urlParams.get('dist') : null
var fromDate = urlParams.has('fromDate') ? decodeURIComponent(urlParams.get('fromDate')) : '6/6/2021'
var toDate = urlParams.has('toDate') ? decodeURIComponent(urlParams.get('toDate')) : '6/14/2021'
var night = urlParams.has('night') ? urlParams.get('night') : false
console.log(night);

// don't forget to include leaflet-heatmap.js
var testData = {
    max: 8,
    data: [{lat: 24.6408, lng: 46.7728, count: 3}, {lat: 50.75, lng: -1.55, count: 1}]
};

var baseLayer = L.tileLayer(
    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '...',
        maxZoom: 18
    }
);

var cfg = {
    // radius should be small ONLY if scaleRadius is true (or small radius is intended)
    // if scaleRadius is false it will be the constant radius used in pixels
    "radius": 2,
    "maxOpacity": .8,
    // scales the radius based on map zoom
    "scaleRadius": true,
    // if set to false the heatmap uses the global maximum for colorization
    // if activated: uses the data maximum within the current map boundaries
    //   (there will always be a red spot with useLocalExtremas true)
    "useLocalExtrema": true,
    // which field name in your data represents the latitude - default "lat"
    latField: 'lat',
    // which field name in your data represents the longitude - default "lng"
    lngField: 'lng',
    // which field name in your data represents the data value - default "value"
    valueField: 'count'
};


var heatmapLayer = new HeatmapOverlay(cfg);

var map = new L.Map('map-canvas', {
    center: new L.LatLng(25.6586, -80.3568),
    zoom: 4,
    layers: [baseLayer, heatmapLayer]
});

heatmapLayer.setData(testData);

$(function () {
    $("#magnitude-rage").slider({
        range: true,
        min: -1,
        max: 6,
        values: [minMag, maxMag],
        step: 0.1,
        slide: function (event, ui) {
            $("#magnitude").val(ui.values[0] + " - " + ui.values[1]);
        }
    });

    $("#magnitude").val($("#magnitude-rage").slider("values", 0) +
        " to " + $("#magnitude-rage").slider("values", 1));

    $("#from").val(fromDate)
    $("#to").val(toDate)
    var dateFormat = "mm/dd/yy",
        from = $("#from")
            .datepicker({
                defaultDate: fromDate,
                changeMonth: true,
                numberOfMonths: 1,
                minDate: "6/6/2021",
                maxDate: "6/14/2021"
            })
            .on("change", function () {
                to.datepicker("option", "minDate", getDate(this));
            }),
        to = $("#to").datepicker({
            defaultDate: toDate,
            changeMonth: true,
            numberOfMonths: 1,
            minDate: "6/6/2021",
            maxDate: "6/14/2021"
        })
            .on("change", function () {
                from.datepicker("option", "maxDate", getDate(this));
            });

    function getDate(element) {
        var date;
        try {
            date = $.datepicker.parseDate(dateFormat, element.value);
        } catch (error) {
            date = null;
        }

        return date;
    }

    $("#lat").val(lat)
    $("#lon").val(lon)
    $("#dist").val(dist)
    night ? $('#night').prop('checked', true) : $('#night').prop('checked', false)
});

function apply() {
    minMag = $("#magnitude-rage").slider("values", 0)
    maxMag = $("#magnitude-rage").slider("values", 1)
    fromDate = $('#from').val()
    toDate = $('#to').val()
    lat = $("#lat").val()
    lon = $("#lon").val()
    dist = $("#dist").val()
    night = $('#night').prop('checked')
    fromDate =
        window.location.replace("/?page=" + page + "&minMag=" + minMag + "&maxMag=" + maxMag
            + "&fromDate=" + encodeURIComponent(fromDate) + "&toDate=" + encodeURIComponent(toDate)
            + "&lat=" + lat + "&lon=" + lon + "&dist=" + dist + "&night=" + night);
}