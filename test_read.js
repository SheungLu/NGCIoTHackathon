function getHeaderTime () {

  var nLastVisit = parseFloat(window.localStorage.getItem('lm_' + this.filepath));
  var nLastModif = Date.parse(this.getResponseHeader("Last-Modified"));

	window.localStorage.setItem('lm_' + this.filepath, Date.now());
	isFinite(nLastVisit) && this.callback(nLastModif, nLastVisit);
	/*
  if (isNaN(nLastVisit) || nLastModif > nLastVisit) {
    window.localStorage.setItem('lm_' + this.filepath, Date.now());
    isFinite(nLastVisit) && this.callback(nLastModif, nLastVisit);
  }*/

}

function ifHasChanged(sURL, fCallback) {
  var oReq = new XMLHttpRequest();
  oReq.open("GET" /* use HEAD - we only need the headers! */, 'sensor_data/sonar/sonarData.csv');
  oReq.callback = fCallback;
  //var theData = oReq.response;
  oReq.filepath = sURL;
  oReq.onload = getHeaderTime;
  oReq.send();
  //return theData; // Note: not oReq.responseText
}

function simpleRead() {
	var oReq = new XMLHttpRequest();
	var X = "No Data";
	oReq.open("GET" /* use HEAD - we only need the headers! */, 'd123');
	//oReq.responseType = 'text';
	oReq.onload = function() {
		var theData = oReq.responseText;
		if (theData) {
			X = theData;
		}
	}
	
	oReq.send();
	return X;
}

function readData (fname,fCallback) {
	var binStr = 'blah';
	var xhr = new XMLHttpRequest();
	//console.log('UNSENT', xhr.readyState); // readyState will be 0

	xhr.open('GET', fname, true);
	//console.log('OPENED', xhr.readyState); // readyState will be 1
	xhr.callback = fCallback;
	xhr.onprogress = function () {
	//console.log('LOADING', xhr.readyState); // readyState will be 3
	};

	xhr.onload = function () {
		//console.log('DONE', xhr.readyState); // readyState will be 4
		binStr = this.responseText;
		//console.log('DONE', xhr.readyState, binStr);
		this.callback(binStr);
	};
	xhr.send(null);
}