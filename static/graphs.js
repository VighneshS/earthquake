var minRange1 = -1
var maxRange1 = 6
var sliders = 0

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
        min: -1,
        max: 6,
        values: [minRange1, maxRange1],
        step: 0.1,
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
    createNewSlider();
    createNewSlider();
    createNewSlider();
    loadChart()
});

function loadChart() {
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
        url: "/graphs",
        contentType: "application/json",
        dataType: 'json',
        data: JSON.stringify(payLoad)
    }).done(function (data) {
        // $(this).addClass("done");
        createChart(data)
    });
}

function createChart(data) {
    d3.selectAll("svg > *").remove();
    var svg = d3.select("svg"),
        margin = 200,
        width = svg.attr("width") - margin,
        height = svg.attr("height") - margin;


    var xScale = d3.scaleBand().range([0, width]).padding(0.4),
        yScale = d3.scaleLinear().range([height, 0]);

    var g = svg.append("g")
        .attr("transform", "translate(" + 100 + "," + 100 + ")");

    xScale.domain(data.map(function (d) {
        return d.magRange;
    }));
    yScale.domain([0, d3.max(data, function (d) {
        return d.value;
    })]);

    g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale));

    g.append("g")
        .call(d3.axisLeft(yScale).tickFormat(function (d) {
            return d;
        }).ticks(10))
        .append("text")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .text("value");

    g.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function (d) {
            return xScale(d.magRange);
        })
        .attr("y", function (d) {
            return yScale(d.value);
        })
        .attr("width", xScale.bandwidth())
        .attr("height", function (d) {
            return height - yScale(d.value);
        });
}