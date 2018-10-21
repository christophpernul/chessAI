"use strict"	
$(document).ready(function() {
	$(".board").click(function(){
		//var data = {"name":"test", "val":"ok"};
		//var json = JSON.stringify(data);
		//var json_2 = "hello";
		//console.log(json);
		//$.post("receiver", json);
		console.log($(this).attr("id"));
		$.post("receiver", JSON.stringify($(this).attr("id")));
		//event.preventDefault();
	});
});

