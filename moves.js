"use strict"	
$(document).ready(function() {
	var moving = $(".board-container").attr("id").charAt(0);
	var nextplayer = $(".board-container").attr("id").charAt(1);

	$("#remis").click(function(){
		console.log("REMIS!");
		$.post("remis", JSON.stringify(moving), function(){window.location = "/remis"});
	});
	$("#resign").click(function(){
		console.log("Resign!");
		$.post("resign", JSON.stringify(moving), function(){window.location = "/resign"});
	});
	$("#newgame").click(function(){
		console.log("Newgame!");
		$.post("newgame", JSON.stringify(moving), function(){window.location = "/newgame"});
	});

	if ( $("#info").text() == " " ) {
        $(".board").click(function () {
            var field = $(this).attr("id");
            // console.log("moving:", moving, "next:", nextplayer);
            // if last character is P then it is a promotion field
            var promote = $(this).attr("class").substr(-1);
            var fieldpiececolor = field.charAt(3);
            var fieldnumber = field.charAt(1);
            if (promote == "P" && fieldpiececolor != moving &&
                ((fieldnumber == "8" && moving == 'w') || (fieldnumber == "1" && moving == 'b'))) {
                document.getElementById("promotion").classList.add("display-boxes");
                $(".boxes").click(function () {
                    var add = $(this).attr("id");
                    //$.post(`${moving}`, JSON.stringify(add+field), function(){window.location = `/${moving}`});
                    $.post("move", JSON.stringify(add + field), function () {
                        window.location = "/move"
                    });
                });
            }
            else {
                //$.post(`${moving}`, JSON.stringify(field), function(){window.location = `/${moving}`});
                $.post("move", JSON.stringify(field), function () {
                    window.location = "/move"
                });
            }
            //event.preventDefault();
        });
    }
});

