"use strict"	
$(document).ready(function() {
	$(".board").click(function(){
		//$(document).querySelector('.btn').style.display = 'none';
		var field = $(this).attr("id");
		var promote = $(this).attr("class").substr(-1);
		console.log($(this).attr("class"), promote, promote=="P");
		if ( promote == "P" ) {
			console.log("Promotion move!");
//			document.getElementsByClassName('.boxes')[0].style.display = 'flex';
			document.getElementById("promotion").classList.add("display-boxes");
			$(".boxes").click(function(){
				var add = $(this).attr("id");
				console.log(add);
				$.post("move", JSON.stringify(add+field), function(){window.location = "/move"});
			});
		}
		else {
			$.post("move", JSON.stringify(field), function(){window.location = "/move"});
		}
		//event.preventDefault();
	});
});

