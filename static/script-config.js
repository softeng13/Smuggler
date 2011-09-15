$(document).ready(function(){
	
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