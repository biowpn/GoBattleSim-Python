
window.GBS = window.GBS || {};
window.UI = window.UI || {};
window.DialogStack = window.DialogStack || [];


GBS.RequestId = 0;
GBS.Processing = 0;
GBS.HostURL = "./";



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


GBS.submit = function(reqType, reqInput, reqOutput_handler, oncomplete) {
	if (GBS.Processing) {
		return;
	}
	GBS.Processing = 1;
	
	var request_json = {
		"reqId": GBS.RequestId,
		"reqType": reqType,
		"reqInput": reqInput
	};
	
	$.ajax({
		url: GBS.HostURL,
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
			if (oncomplete) {
				oncomplete();
			}
		}
	});
}


