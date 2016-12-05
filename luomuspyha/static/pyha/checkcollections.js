var accepted = [];
var acceptedsens = 0;
function checksens() { 
  approvetext = "{% trans 'you_accepted_terms' %}";
  nonapprovetext = "{% trans 'you_have_not_accepted_terms' %}";
  if(document.getElementById('checkbsens').checked){
	  document.getElementById('statustextsens').textContent=approvetext;
	  acceptedsens = 1;
  }else{
	  document.getElementById('statustextsens').textContent=nonapprovetext;
	  acceptedsens = 0;
}
}
function check(counter) { 
  approvetext = "{% trans 'you_accepted_terms' %}";
  nonapprovetext = "{% trans 'you_have_not_accepted_terms' %}";
  if(document.getElementById('checkb'+ counter).checked){
	  document.getElementById('statustext'+ counter).textContent=approvetext;
	  document.getElementById('acc' + counter).hidden = true
	  accepted[counter] = 1;
  }else{
	  document.getElementById('statustext'+ counter).textContent=nonapprovetext;
	  document.getElementById('acc' + counter).hidden = false
	  accepted[counter] = 0;
}
}
function checkv(counter, value) { 
  accepted[counter] = value;
}
function checkForApproval(){
var approved = 0;
for (i = 0; i < accepted.length; i++){
	approved += accepted[i];
}
approved += acceptedsens;
if(approved == accepted.length + 1){
	document.getElementById('submit').disabled = false;
	document.getElementById('submitstatustext').hidden = true;
	document.getElementById('collections_not_approved').hidden = true;
}else{
	document.getElementById('submit').disabled = true;
	document.getElementById('submitstatustext').hidden = false;
	document.getElementById('collections_not_approved').hidden = false;
}
}