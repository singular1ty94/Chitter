/*
** CHITTER Core Javascript File
** MIT License
** Kannon Chan (k9chan)
** Brett Orr (singular1ty94)
*/
$(function() {
	run = false;
	tweets = [];
	var timer;
	var cloud;

	positive = 0;
	negative = 0;
	
	$('.shaft-load3').hide();
    
    /**
    * A long-polling function that fetches
    * a tweet in JSON format from the server.
    * This is a stripped JSON object, ie, it does
    * not contain the full twitter JSON data.
    */
    function poll() {
        timer = setTimeout(function() {
            if(run){

            $.ajax({ url: "/stream", success: function(data) {
                try{
                	$('.shaft-load3').hide();
					//Check the sentiment
					if(data.sentiment == 1){
                        positive++;
						sent = "positive";
                    }else{
                        negative++;
						sent = "negative";
                    }
					//Get the hashtags and make the clickable.
					var arr = data.text.match(/[#][a-zA-Z]+/g);
					var text = data.text;
					for (var item in arr){
						text = text.replace(arr[item], "<a href=\"#\" data-hashtag=\"" + arr[item].substring(1, arr[item].length) + "\">" + arr[item] + "</a>");
					}
					
					//Get the hyperlinks
					arr = text.match(/(http:\/\/)[a-zA-Z.0-9\/]+/g);
					for (var item in arr){
						text = text.replace(arr[item], "<a href=\"" + arr[item] + "\" target=\"_blank\">" + arr[item] + "</a>");
					}
					
					//Now the twitter handles.
					arr = text.match(/(@)[a-zA-Z0-9_]+/g);
					for (var item in arr){
						text = text.replace(arr[item], "<a href=\"" + arr[item] + "\" target=\"_blank\">" + arr[item] + "</a>");
					}
					
					//Inject it.
                    $('#twitter').prepend("<p class=\"triangle-border " + sent + "\">"+
					"<img src=\"" + data.profile + "\" alt=\"\" />" + text + data.sentiWord + "</p>");
					
					//Register listener
					$('#twitter a').click(function(){
						$("#searchTerm").val($(this).data('hashtag'));
						stop();
						$("#cloud").html("");
						start();
					});
					
					//Update chart
                    updateChart();
                }catch(e){
                }
            }, dataType: "json", complete: poll });   
            }
        }, 50);
    }
    
    /**
    * Long-polling function that loads the word
    * cloud from the server.
    */
    function tagCloud() {
		cloud = setTimeout(function() {
		    if(run){
				$.ajax({ url: "/cloud", success: function(data) {
					$("#cloud").html();
					$("#cloud").html(data);
					
					//With the data, now we can do stuff.
					$('#cloud a').click(function(){
						$("#searchTerm").val($(this).data('hashtag'));
						stop();
						$("#cloud").html("");
						start();
					});
					
				}, fail: function(data){
				
				},complete: tagCloud });   
		    }
		}, 1000);
	}

    
	/**
	* Clears the private variables.
	* Starts a new session.
	*/ 
	function start(){
		if($("#searchTerm").val()!=""){
			$('.shaft-load3').show();
	        $.get('/prepare?search=' + $("#searchTerm").val(), function(data) {
	            //Now we set it to go.
	        });
	        run = true;
	        poll();
	        tagCloud();
	    }
	}

	/**
	* Starts the search.
	*/
	$('#searchBtn').click(function(){
		start();
	});


	// Added enter key runs stream
	$(document).keypress(function(e) {
		if(e.which == 13) {
			start();
		}
	});

	/**
	* Stops the search from running.
	*/
	$('#stopBtn').click(function(){
		stop();
	});
	
	/**
	* Stops the search from running.
	*/
	function stop(){
	    //Stop!
        $.get('/stop', function(data){
        
        });
        clearTimeout(timer);
        clearTimeout(cloud);
        run = false;
		//Hide loading wheel
		$('.shaft-load3').hide();
	}
	
	/**
	* OVERKILL - Polls down to yes > /dev/null
	*/
	var overkill = false;
	$("#overkill").click(function(){
		//Double check you want to do this.
		if(!overkill){
			if(confirm("Start the Overdrive?")){
				//Starting.
				$.get('/overkill', function(data) {
					//Now we set it to go.
				});
				overkill = true;
				$(this).html("Stop Overdrive");
				alert("Overdrive On.");
			}
		}else{
			if(confirm("Stop the Overdrive?")){
				//Stop it.
				$.get('/stopOverkill', function(data) {
					//Wind it down boys.
				});
				overkill = false;
				$(this).html("Overdrive");
				alert("Overdrive Off.");
			}
		}
	});

	/**
	* Make the chart appear or disappear.
	*/
	$('#GraphBtn').click(function(){	
  		$('#chart').slideToggle("fast");
  		$('#cloud').slideToggle("fast");
	});

	/**
	* Clear the screen and searches.
	*/
	$('#clearBtn').click(function(){
		if(!run){
			
			positive = 0;
			negative = 0;
			resetChart();
			

			$('#searchTerm').val("");
			$('#twitter').html("");
			$('.shaft-load3').hide();
			
			$("#cloud").html("");
			
			$.get("/clear", function(data){
			
			});
		}
	});

///////////////////////
//CHARTING FUNCTIONS //
//////////////////////
	/**
	* Resets the chart to nothing.
	*/ 
	var chart;

	function resetChart(){	
	chart = c3.generate({
		data: {
			columns: [	            
				['Negative', 1],
				['Positive', 1]
			],
			type : 'pie',
			 colors: {
				Positive: '#5CB85C',
				Negative: '#d9534f',
			},
		},

		pie:{
			label:{
		   	    format:function(x){ 
		   	    	//display 0,0 at beginning of load
		   		   if (positive == 0 && negative == 0){
		   			  return 0;
				   } else {
		   			return x;
				   }
				}
			}
		},		   

		tooltip: {
			format: {
			 value: d3.format('s') // apply this format to both y and y2
			},
			show: true
		},

		legend: {
			show: false
		},

		donut: {
			title: "Sentiment"
		}

	});

	}

	/**
	* Updates chart with global variables.
	*/ 
	function updateChart(){
		chart.load({
		  columns: [		   
		    ["Negative", negative],
		    ["Positive", positive],
  		]
		});
	}

	resetChart();




});
