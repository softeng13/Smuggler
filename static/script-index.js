$(document).ready(function(){
	
	$("#fullscan").click(function(e) {
		e.preventDefault();
	    
	    $.getJSON('json/fullscan', function(data) {
	    	$.each(data, function() {
	    		  $.sticky(this);
	    	});

	    });
	});

	$("#localscan").click(function(e) {
		e.preventDefault();
	    
	    $.getJSON('json/localscan', function(data) {
	    	$.each(data, function() {
	    		  $.sticky(this);
	    	});

	    });
	});

	$("#smugmugscan").click(function(e) {
		e.preventDefault();
	    
	    $.getJSON('json/smugmugscan', function(data) {
	    	$.each(data, function() {
	    		  $.sticky(this);
	    	});

	    });
	});
	
	//loops to check for messages
	setInterval(function(){
		$.getJSON('json/notify', function(data) {
	    	$.each(data, function() {
	    		$.each(this, function(k, v) {
	    			if (k == 'message')
	    				$.sticky(v);
	    		  });
	    		
	    	});

	    });
	}, 10000);

});