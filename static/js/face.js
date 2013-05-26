var fb_username = '';

function getParameterByName( name, href )
{
	if (href === undefined || href === null)
		href = window.location;
	name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
	var regexS = "[\\?&]"+name+"=([^&#]*)";
	var regex = new RegExp( regexS );
	var results = regex.exec( href );
	if( results === null )
		return null;
	else
		return decodeURIComponent(results[1].replace(/\+/g, " "));
}


function load_startup_data() {
	console.log('load_startup_data');
}


function facebook_login_callback(response) {
    if (response.authResponse) {
		console.log('Welcome!  Fetching your information.... ');
		var access_token = FB.getAuthResponse()['accessToken'];
		console.log('Access Token = '+ access_token);
		$.get('/fbget', {'token': access_token});

		FB.api('/me', function(response) {
			console.log('Good to see you, ' + response.first_name + '.');
			fb_username = response.username;
			refresh();
		});
	} else {
		console.log('User cancelled login or did not fully authorize.');
	}
}


function refresh() {
	$.get('/refresh', {'fb_username': fb_username}, function(response) {
		console.log(response);
	});
}


function setUpMainPageEvents() {
	console.log('setUpMainPageEvents');
	$(".fblogin").click(function () {
		console.log('clicked!');
		FB.login(facebook_login_callback, {scope: 'read_stream'});
	});
}


function startupLoadStep1() {
	console.log("startupLoadStep1");
	var limit = 30;
	var nb_per_line = 3;
	var container = $(".container");
	var line_tmpl = "<div class='row-fluid' />";
	var line;
	$.getJSON('/all_unknown', {limit: 30}).done(function (response) {
		console.log("answer");
		$.each(response.data, function (idx, picture) {
			console.log(idx);
			console.log(picture.url);
			console.log(picture.facebook_id);
			if (idx % nb_per_line === 0) {
				container.append(line);
				line = $(line_tmpl);
			}
			var imgdiv = $("<div />");
			imgdiv.attr('class', 'span' + 12/nb_per_line);
			var img = $("<img />");
			img.attr('src', picture.url);
			img.attr('id', 'img_' + picture.facebook_id);
			var okButton = $("<button />");
			okButton.html("CONFIRMER");
			okButton.attr('action-type', 'confirm');
			okButton.attr('facebook_id', picture.facebook_id);
			var badButton = $("<button />");
			badButton.html("SUPPRIMER");
			badButton.attr('action-type', 'delete');
			badButton.attr('facebook_id', picture.facebook_id);
			imgdiv.append(img);
			imgdiv.append(okButton);
			imgdiv.append(badButton);
			line.append(imgdiv);
		});
		$("button").click(function () {
			var facebook_id = $(this).attr('facebook_id');
			var action = $(this).attr('action-type');
			var url = '/';
			if (action == 'confirm')
				url += 'confirm_raw_picture';
			else if (action == 'delete')
				url += 'detach_raw_picture';
			else
				return false;
			$.post(url, {'facebook_id': facebook_id}).done(function (response){
				console.log("confirmed req");
			});
		});
	});
}


function startupLoadStep2() {

}