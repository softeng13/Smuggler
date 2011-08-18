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
	
	if ($("#root_dir").val() == ''){
		$.getJSON('json/rootdir', function(data) {
	    	$.each(data, function() {
	    		$("#root_dir").val(data)
	    	});
	    });
	}
	
	if ($("#log_dir").val() == ''){
		$.getJSON('json/logdir', function(data) {
	    	$.each(data, function() {
	    		$("#log_dir").val(data)
	    	});
	    });
	}
	
	if ($("#data_dir").val() == ''){
		$.getJSON('json/datadir', function(data) {
	    	$.each(data, function() {
	    		$("#data_dir").val(data)
	    	});
	    });
	}
		
		
		
});