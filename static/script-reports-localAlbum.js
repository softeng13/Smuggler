$(document).ready(function(){
	
	//loops to check for messages
	setInterval(function(){
		$.getJSON('/json/notify', function(data) {
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

	
	$.get("/table/localAlbumTable", function(data) {
		$("#spinner").css("display", "block");
        $("#results").append(xml_to_string(data));
        $("#spinner").css("display", "none");
    });


});