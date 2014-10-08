/*
** CHITTER Core Javascript File
** MIT License
** Kannon Chan (k9chan)
** Brett Orr (singular1ty94)
*/
$(function() {
	run = false;
	tweets = [];
	var myVar;
	var cloudVar;
	searchTerm = "";
	positive = 0;
	negative = 0;
	var wordAssoc = {};
	
	$('.shaft-load3').hide();

	/**
	* Function that takes a given tweet,
	* strips its characters, returns the
	* sentiment from the server,
	* and updates the page.
	*/
	function update(tweet) {
		if (run && tweets.length > 0){	
    		//Once tweets reach 20, load more
		    if(tweets.length == 20){
				setTimeout(getTweets(),0);
			}

			//remove special characters from tweet and urls
			tweet.text = tweet.text.replace(/http.[^\s]+/g, "");
			tweet.text = tweet.text.replace(/www.[^\s]+/g, "");
			tweet.text = tweet.text.replace(/.[^\s]+com/g, "");
			tweet.text = tweet.text.replace(/[^a-zA-Z ]/g, "");

			if(tweet.hashtags.length > 0){		
				updateTags(tweet.hashtags);
			}

	
			//Retreive the Sentiment from the Server for just this tweet. 
		  	$.get('/streamREST?text='+ tweet.text, function(data) {
		  		//Use the sentiment returned to us from the server.
  				if(JSON.parse(data) == 1){
					sentiWord = "<span class = 'positive'> Positive</span>";
					positive ++;
				} else {
					sentiWord = "<span class = 'negative'> Negative</span>";
					negative ++;
				}

        		//Display it and update the chart.
				$('#twitter').prepend("<br /><br />" +  tweet.text + sentiWord);
				updateChart();
			});
		}
	}

	/**
	* Updates the cloud of hashtags.
	*/
	function updateTags(hashtags){
		for(var i = 0; i < hashtags.length; i++){
			if(!wordAssoc[hashtags[i].text]){
				wordAssoc[hashtags[i].text] = 1;
			}else{
				wordAssoc[hashtags[i].text] += 1;
			}
		}
	}
	/**
	* Function that extracts the search term and
	* sets the getTweet loop into motion.
	*/ 
	function prepare(){
		if(run && $('#searchTerm').val() != ""){
			searchTerm = $('#searchTerm').val();	  		
			getTweets();				
		}
	}

	/**
	* Calls the server to give us 100
	* tweets, which contain the text of 
	* the tweet only.
	*/ 
	function getTweets(){
		//Show the symbol if we're still loading or about to load.
    	if (tweets.length < 20){
			$('.shaft-load3').show();
    	}

		$.get('/rest?search=' + searchTerm, function(data){
			clearInterval(myVar);
			clearInterval(cloudVar);
			        
			//adds to current stack of tweets
			tweets.push.apply(tweets,JSON.parse(data));

			//Hide the shaft
			$('.shaft-load3').hide();
		
			//Call update at interval of 1000 milliseconds
			myVar = setInterval(function(){update(tweets.pop())}, 1000);
			cloudVar = setInterval(function(){updateCloud()}, 2300);
			
		});	
	}
	
	/**
	* Clears the private variables.
	* Starts a new session.
	*/ 
	function start(){
		clearInterval(myVar);
		clearInterval(cloudVar);

		//resets tweets if new search term is entered
		if (searchTerm!=$('#searchTerm').val()){
			tweets = [];
		}

		run = true;
		if (tweets.length == 0){
			prepare();
		} else {
			myVar = setInterval(function(){update(tweets.pop())}, 1000);
			cloudVar = setInterval(function(){updateCloud()}, 2000);
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
		clearInterval(myVar);
		clearInterval(cloudVar);
		run = false;

		//Hide loading wheel
		$('.shaft-load3').hide();

	});

	/**
	* Make the chart appear or disappear.
	*/
	$('#GraphBtn').click(function(){	
  		$('#chart').slideToggle("fast");	 	
	});

	/**
	* Clear the screen and searches.
	*/
	$('#clearBtn').click(function(){
		if(!run){
			resetChart();
			resetCloud();

			positive = 0;
			negative = 0;

			$('#searchTerm').val("");
			$('#twitter').html("");
			$('.shaft-load3').hide();
		}
	});

///////////////////////
//CHARTING FUNCTIONS //
//////////////////////
	/**
	* Resets the chart to nothing.
	*/ 
	function resetChart(){	

		chart.load({
	  		columns: [
				["Negative", 1],
				["Positive", 1],
	  		]
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

	var chart = c3.generate({
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
			}
		},

		legend: {
			show: false
		},

		donut: {
			title: "Sentiment"
		}

	});

////////////////
// WORD CLOUD //
////////////////
	var fill = d3.scale.category20b();
	var rendering = false;


	function draw(words) {
		d3.select("#cloud").append("svg")
		.attr("width", 300)
		.attr("height", 300)
		.append("g")
		.attr("transform", "translate(150,150)")
		.selectAll("text")
		.data(words)
		.enter().append("text")
		.style("font-size", function(d) { return d.size + "px"; })
		.style("font-family", "Impact")
		.style("fill", function(d, i) { return fill(i); })
		.attr("text-anchor", "middle")
		.attr("transform", function(d) {
			return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
		}).text(function(d) { 
			return d.text; 
		});
		rendering = false;
	}

	
	function updateCloud(){
	
		if(!rendering){
			rendering = true;
			var myNode = document.getElementById("cloud");
			while (myNode.firstChild) {
				myNode.removeChild(myNode.firstChild);
			}
			
			d3.layout.cloud().size([300, 300])
			.words(Object.keys(wordAssoc)
			.map(function(d) {
				return {text: d, size: wordAssoc[d]*20};
			}))
			.padding(5)
			.rotate(function() { return ~~(Math.random() * 2) * 90; })
			.font("Impact")
			.fontSize(function(d) { return d.size; })
			.on("end", draw).start();
			}
		}
		
	function resetCloud(){
		var myNode = document.getElementById("cloud");
		while (myNode.firstChild) {
			myNode.removeChild(myNode.firstChild);
		}
		rendering = false;
		wordAssoc = {};
	}
});
