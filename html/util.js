
var GBS = {};
var UI = {};
var DialogStack = [];


GBS.RequestId = 0;
GBS.Processing = 0;
var HostURL = "./";



function try_parse(v) {
	if (isNaN(parseFloat(v))) {
		return v;
	} else {
		return parseFloat(v);
	}
}


UI.sendFeedbackDialog = function(message, dialogTitle, onOK){
	var d = $("<div>")
	.text(message)
	.attr("title", dialogTitle || "")
	.dialog({
		buttons: {
			"OK": function(){
				$(this).dialog("close");
				if (onOK) {
					onOK();
				}
			}
		}
	});
	DialogStack.push(d);
}


GBS.submit = function(reqType, reqInput, reqOutput_handler, no_dialog) {
	if (GBS.Processing) {
		if (!no_dialog) {
			UI.sendFeedbackDialog("Request already pending");
		}
		return;
	}
	GBS.Processing = 1;
	if (!no_dialog) {
		UI.sendFeedbackDialog("Running...");
	}
	
	var request_json = {
		"reqId": GBS.RequestId,
		"reqType": reqType,
		"reqInput": reqInput
	};
	
	$.ajax({
		url: HostURL,
		type: "POST",
		dataType: "json",
		data: JSON.stringify(request_json),
		processData: false,
		success: function(resp){
			while (DialogStack.length > 0) {
				DialogStack.pop().dialog('close');
			}
			reqOutput_handler(resp["reqOutput"]);
		},		
		error: function(jqXHR, textStatus, errorThrown){
			while (DialogStack.length > 0) {
				DialogStack.pop().dialog('close');
			}
			UI.sendFeedbackDialog(errorThrown);
		},
		
		complete: function(){
			GBS.RequestId++;
			GBS.Processing = 0;
		}
	});
}


