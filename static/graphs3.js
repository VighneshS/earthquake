var minRange1 = 10104
var maxRange1 = 1900081
var step = 100
var sliders = 0
var spinner
var figure

function createNewSlider() {
    const rangeSliders = $('#range-sliders')
    const $label = $("<label for=\"range" + (sliders + 1) + "\"></label>").text('Range ' + (sliders + 1) + ':');
    const $br = $('<br>');
    const $input = $('<input type="text" readonly style="border:0; color:#f6931f; font-weight:bold;"/>').attr({
        id: "range" + (sliders + 1)
    });
    var $div = $('<div></div>').attr({id: 'range' + (sliders + 1) + '-rage'});
    var $container = $('<div></div>').attr({id: 'range' + (sliders + 1) + '-container'});

    $label.appendTo($container)
    $br.appendTo($container)
    $input.appendTo($container)
    $div.appendTo($container)
    $br.appendTo($container)
    rangeSliders.append($container)

    var sliderNumber = (sliders + 1)

    $("#range" + (sliders + 1) + "-rage").slider({
        range: true,
        min: minRange1,
        max: maxRange1,
        values: [minRange1, maxRange1],
        step: step,
        slide: function (event, ui) {
            $("#range" + sliderNumber).val(ui.values[0] + " - " + ui.values[1]);
        }
    });
    $("#range" + sliderNumber).val($("#range" + sliderNumber + "-rage").slider("values", 0) +
        " to " + $("#range" + sliderNumber + "-rage").slider("values", 1));
    ++sliders
}

function deleteSlider() {

    $("#range" + (sliders) + "-container").remove()
    --sliders
}

$(function () {
    spinner = $('#spinner')
    figure = $('#figure')
    spinner.show()
    figure.hide()
    createNewSlider();
    loadChart()
});

function loadChart() {
    spinner.show()
    figure.hide()
    var payLoad = []
    for (let i = 0; i < sliders; i++) {
        var range_slider = $("#range" + (i + 1) + "-rage")
        payLoad.push({
            'from': range_slider.slider("values", 0),
            'to': range_slider.slider("values", 1)
        })
    }
    $.ajax({
        type: 'POST',
        url: "/graphs/3",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad[0])
    }).done(function (data) {
        createChart(data)
        spinner.hide()
        figure.show()
    });
}

function createChart(data) {
    Highcharts.chart('bar-chart', {
        chart: {
            height: "50%",
            type: 'scatter',
            zoomType: 'xy'
        },
        title: {
            text: 'VN = (Volcano Number / 1000 ) vs Longitude for Volcanoes'
        },
        subtitle: {
            text: 'Scatter plot'
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'VN = (Volcano Number / 1000 )'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Longitude'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            verticalAlign: 'top',
            x: 100,
            y: 70,
            floating: true,
            backgroundColor: Highcharts.defaultOptions.chart.backgroundColor,
            borderWidth: 1
        },
        plotOptions: {
            scatter: {
                marker: {
                    radius: 5,
                    states: {
                        hover: {
                            enabled: true,
                            lineColor: 'rgb(100,100,100)'
                        }
                    }
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x}, {point.y}'
                }
            }
        },
        series: [{
            name: 'VN = (Volcano Number / 1000 ) vs Longitude for Volcanoes',
            color: 'rgba(223, 83, 83, .5)',
            data: data

        }]
    });
}