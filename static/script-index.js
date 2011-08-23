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
	
	function xml_to_string(xml_node)
    {
        try {
			if (xml_node.xml)
	            return xml_node.xml;
	        else if (XMLSerializer)
	        {
	            var xml_serializer = new XMLSerializer();
	            return xml_serializer.serializeToString(xml_node);
	        }
	        else
	        {
	            alert("ERROR: Extremely old browser");
	            return "";
	        }
        } catch (e){
        	alert ("ERROR")
        	return ""
        }
    }
	

	$.get("/sync/newCategories", function(data) {
		if (xml_to_string(data).indexOf('parsererror') != -1){
			$("#new_categories").addClass("hidden");
		} else {
			$("#new_categories").append(xml_to_string(data));
		}
    });
        
	
	$.get("/sync/newSubCategories", function(data) {
		if (xml_to_string(data).indexOf('parsererror') != -1){
			$("#new_subcategories").addClass("hidden");
		} else {
			$("#new_subcategories").append(xml_to_string(data));
		}
    });
	
	$.get("/sync/newAlbums", function(data) {
		if (xml_to_string(data).indexOf('parsererror') != -1){
			$("#new_albums").addClass("hidden");
		} else {
			$("#new_albums").append(xml_to_string(data));
		}
    });

});