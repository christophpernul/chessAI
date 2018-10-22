"use strict"	
$(document).ready(function() {
	$(".board").click(function(){
		console.log($(this).attr("id"));
		$.post("move", JSON.stringify($(this).attr("id")), function(){window.location = "/move"});
		//event.preventDefault();
	});
});

