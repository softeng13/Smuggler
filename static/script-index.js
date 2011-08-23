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
    }
	
	
	$.get("/sync/newCategories", function(data) {
		$("#new_categories").append(xml_to_string(data));
    });
        
	
	$.get("/sync/newSubCategories", function(data) {
		$("#spinner").css("display", "block");
        $("#new_subcategories").append(xml_to_string(data));
        $("#spinner").css("display", "none");
    });
	
	$.get("/sync/newAlbums", function(data) {
		$("#spinner").css("display", "block");
        $("#new_albums").append(xml_to_string(data));
        $("#spinner").css("display", "none");
    });

});