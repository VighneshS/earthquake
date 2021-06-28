var spinner
var figure

$(function () {
    spinner = $('#spinner')
    figure = $('#figure')
    spinner.show()
    figure.hide()
    loadChart()
});

function loadChart() {
    spinner.show()
    figure.hide()
    var payLoad = {
        'numberOfItems': $('#numberOfRecent').val()
    }
    $.ajax({
        type: 'POST',
        url: "/graphs/2",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
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
            text: 'Magnitude vs Depth of Recent Earthquake data'
        },
        subtitle: {
            text: 'Scatter plot'
        },
        xAxis: {
            title: {
                enabled: true,
                text: 'Magnitude'
            },
            startOnTick: true,
            endOnTick: true,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Depth'
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
                    pointFormat: '{point.x}, {point.y} kg'
                }
            }
        },
        series: [{
            name: 'Magnitude vs Depth',
            color: 'rgba(223, 83, 83, .5)',
            data: data

        }]
    });
}