/*
:)
*/
var diameter = 650;
var newcat = "all";
var state1 = true;
var state2 = true;
var state3 = true;

// create chart svg space
var svg = d3.select('svg')
	.attr('width', diameter+350)
	.attr('height', diameter)
    .attr('margin-top', 200);

//

// invoke pack layout and misterious filtering
var bubble = d3.layout.pack()
    .sort(compa)
	.size([diameter, diameter])
	.padding(8) // padding between adjacent circles
	.value(function(d) {return d.size;}); // new data will be loaded to bubble layout



// ---------------- ---------------- DRAW BUBBLES ----------------- --------------//
function drawBubbles(newcat){
    var bop = svg.selectAll('g')
        .data({}, function(d) {return d;});
        bop.exit().remove();
    
    var tooltip = d3.select("#tooltip");

    var nodes = bubble.nodes(processData(data[newcat]))
	    .filter(function(d) { return !d.children; }); // filter out the outer bubble 
    console.log(data[newcat]);

    //create groups for each, append circle and text
    var vis = svg.selectAll('g')
	    .data(nodes, function(d) {return d.name;})
	    .enter().append('g')
        .attr('transform', function(d) { 
            //this is the random distributer
            return 'translate(' + (1.1*d.x+100+(Math.random()-0.4)*50) + ',' + (1*d.y +(Math.random()-0.5)*10) + ')'; 
        })
        .attr('cx', function(d){return d.x})
        .attr('cy', function(d){return d.y})
        ;

    vis.append('circle') 
	    //.attr('r',0)
        .attr('value', function(d) { return 1.1*d.r+((Math.random()-0.4) * 10); }) //this is the random size add
	    .attr('class', function(d) { return sizeToClass(d.value)+' bubble'; })
        .attr('opacity', 0)
        .attr('catname', function(d) { return d.name; })
        .on("mouseover", function(d) {
            tooltip.text(d.name + ": " + d.value);
            tooltip.style("visibility", "visible");
            // get to front
            this.parentNode.parentNode.appendChild(this.parentNode);
        })
        .on("mousemove", function() {
            return tooltip.style("top", (d3.event.pageY-20)+"px").style("left",(d3.event.pageX+10)+"px");
        })
        .on("mouseout", function(){
            return tooltip.style("visibility", "hidden");
        });

    vis.append("text")
        .attr("dy", ".3em")
        .attr('class', function(d) { return sizeToClass(d.value); })
        .attr('opacity', 0)
        .style("text-anchor", "middle")
        .style("fill", "#FFFFFF")
        .style("pointer-events", "none")
        .text(function(d) { 
            if (d.name.length > 9){
                return d.name.substr(0,9).concat("…")
            } else{
            return d.name; 
            }
        });
    
    // add the div containers for tooltips with custom content
    vis.append("div")
        .attr("class", "hidden")
        .text(function(d) { return tts[newcat][d.name]; });
    
    //$('circle').animate().toggle().toggle();
    $('.bubble').each(function() {
        var nr = $(this).attr('value');
        $(this).animate({
            r: nr,
            opacity: 0.90
            }, {
                duration: Math.random()*2100,
                step: function(now){
                        // others are cool and go throu this
                        $(this).attr('r', now);
                        // firefox is stupid and need this
                        $(this).attr('r', nr);
                    }
            });
    });

    //anima el aumento de opacidad del texto
    $('text').animate({
            opacity: 1,
    }, 500+Math.random()*1300);

    // then create the qtips
    $(".bubble").each(function(){
        var cir = $("#circe");
        $(this).qtip({
            show: 'click',
            hide:'unfocus',
            content:{
                text: $(this).siblings('div').text()
            },
            style: {
                classes: 'qtip qtip-rounded qtip-mx',
                width: '300px',
                def: 'false',
            },
            position: {
                my: 'center left',  // Position my top left...
                at: 'center right', // at the bottom right of...
                target: $(this) // my target
            }
        });
        /*/ this is for circe
        $(this).on({
            mouseover: function(){
                cir.css($(this).offset());
                cir.css("visibility", "visible");
                },
            mouseout: function(){
                return cir.css("visibility", "hidden");
            }
        });*/
    }); // end of circle selector

};  // end of function




// ---------------- ---------------- FUNCTIONS ----------------- --------------//
function compa(a, b) {
  return (Math.random()*Math.random()-0.5);
}


function processData(pata) {
	var obj = pata;
	var newDataSet = []; 
    //console.log(pata);
	for(var prop in obj) {
		newDataSet.push({name: prop, className: prop.toLowerCase(), size: obj[prop]});
	}
	console.log("[:P]: "+obj);
    //console.log(newDataSet);
	return {children: newDataSet};
}


function changeCategory() {
    newcat = document.getElementById("categoria").value;
    console.log('[Updating to]: ' + newcat);
    drawBubbles(newcat);
    }



function sizeToClass(ra){
    if (ra < 100) return "burb1";
    if (ra>=100 && ra < 200) return "burb2";
    if (ra>=200 && ra < 300) return "burb3";
    if (ra>=300 && ra < 400) return "burb4";
    if (ra>=400 && ra < 500) return "burb5";
    if (ra>=500) return "burb6";
    else return "burb0";
}



// ---------------- ---------------- MAIN ----------------- --------------//
var main = function (){
    
    drawBubbles(newcat);

    // draw the colorstrip below nav
    $('#colorstrip').colorstrip({
        minInterval: 2000,
        maxInterval: 11000,
        minWidth: 20,
        maxWidth: 60,
        opacity: 0.5,
        //colors: ['#f90', '#39c', '#c00', '#090', '#c3f', '#007', '#69f']
        //colors: ['#FFD7C0', '#FFA67B', '#FF6446', '#D3D3D2', '#8C8C8B' ,'#B6B7B5']
        colors: ['#8C8C8B', '#FF6446', '#D3D3D2', '#FFA67B', '#FF6446']
    });

    // click on nav event handler
    $(".selec").on('click', function(e){
        e.preventDefault();
        //$(this).tab('show');
        var categ = $(this).attr('value');
        console.log('[Updating to]: ' + categ);
        drawBubbles(categ);

        $('.selec.active').removeClass('active');
        var $this = $(this);
        if (!$this.hasClass('active')){
            $this.addClass('active');
        }
        e.preventDefault();
    });
 
    // hidden textes
    $("#ltodo").hover(function(){
        $('.txtodo').removeClass('hidden');
    }, function(){
        $('.txtodo').addClass('hidden');
    });
    $("#lejec").hover(function(){
        $('.txejec').removeClass('hidden');
    }, function(){
        $('.txejec').addClass('hidden');
    });
    $("#ldipu").hover(function(){
        $('.txdipu').removeClass('hidden');
    }, function(){
        $('.txdipu').addClass('hidden');
    });
    $("#lsena").hover(function(){
        $('.txsena').removeClass('hidden');
    }, function(){
        $('.txsena').addClass('hidden');
    });
    $("#lgobe").hover(function(){
        $('.txgobe').removeClass('hidden');
    }, function(){
        $('.txgobe').addClass('hidden');
    });
    $("#lopin").hover(function(){
        $('.txopin').removeClass('hidden');
    }, function(){
        $('.txopin').addClass('hidden');
    });
    $("#lpri").hover(function(){
        $('.txpri').removeClass('hidden');
    }, function(){
        $('.txpri').addClass('hidden');
    });
    $("#lpan").hover(function(){
        $('.txpan').removeClass('hidden');
    }, function(){
        $('.txpan').addClass('hidden');
    });
    $("#lprd").hover(function(){
        $('.txprd').removeClass('hidden');
    }, function(){
        $('.txprd').addClass('hidden');
    });


    // icon-check
    $("#icon-check").on({
        click: function (e) {
            $("#text-check").show();
            $('#infoblock-check').animate({right: 40}, 200);
            $('#infoblock-check').animate({width: 230}, 200);
            $("#text-check" ).position({
                my: "center-50 top+2",
                at: "center top",
                of: "#infoblock-check"
            });
            $( "#text-check" ).animate( {opacity: 1}, 500);
            e.preventDefault();
        },
        blur: function() {
            $("#text-check").hide();
            $('#infoblock-check').animate({width: 55}, 200);
            $('#infoblock-check').animate({right: -120}, 200);
            $( "#text-check" ).animate( {opacity: 0}, 300);
        }
    });
    
    // icon-info
    $("#icon-info").on({
        click: function (e) {
            $("#text-info").show();
            $('#infoblock-info').animate({right: 40}, 200);
            $('#infoblock-info').animate({width: 230}, 200);
            $("#text-info" ).position({
                my: "center-50 top+2",
                at: "center top",
                of: "#infoblock-info"
            });
            $( "#text-info" ).animate( {opacity: 1}, 500);
            e.preventDefault();
        },
        blur: function() {
            $("#text-info").hide();
            $('#infoblock-info').animate({width: 55}, 200);
            $('#infoblock-info').animate({right: -120}, 200);
            $( "#text-info" ).animate( {opacity: 0}, 300);
        }
    });

    // modal-ethos
    $('.logo-ethos').on('click', function ( e ) {
        Custombox.open({
            target: '#modal-eth',
            effect: 'slide',
            overlayOpacity: 0.85 
        });
        e.preventDefault();
    });


    // modal-method
    $('#text-metod').on('click', function ( e ) {
        Custombox.open({
            target: '#modal-metod',
            effect: 'slide',
            overlayOpacity: 0.85
        });
        e.preventDefault();
    });
}


// ---------------- ---------------- Execute ----------------- --------------//
$(document).ready(main);