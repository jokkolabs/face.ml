var fb_username = '';
var ias;
var DEFAULT_FACE_SIZE = 200;


function pageReload() {
    window.location.reload(true);
}

function createFaceImg(picture, face_size) {
    if (face_size === null || face_size === undefined)
        face_size = DEFAULT_FACE_SIZE;
    var new_width = Math.floor(picture.source_width * face_size / picture.face_width);
    var new_height = Math.floor(picture.source_height * face_size / picture.face_height);
    var margin_left = -Math.floor(new_width * picture.face_x / picture.source_width);
    var margin_top = -Math.floor(new_height * picture.face_y / picture.source_height);

    var imgDiv = $("<div />");
    imgDiv.attr('picture_id', picture.picture_id);
    imgDiv.attr('class', 'facecontainer');
    imgDiv.css('width', face_size);
    imgDiv.css('height', face_size);

    var img = $('<img />');
    img.attr('picture_id', picture.picture_id);
    img.attr('src', picture.url);
    img.css('margin-left', margin_left);
    img.css('margin-top', margin_top);
    img.attr('width', new_width);
    img.attr('height', new_height);
    imgDiv.append(img);

    return imgDiv;
}

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
    refresh();
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
        $("#winner_pic").html(createFaceImg(response.data.winner, 250));
        $("#left_pic").html(createFaceImg(response.data.left));
        $("#right_pic").html(createFaceImg(response.data.right));
        $("#nbvoteright").html(response.data.right.nb_votes);
        $("#nbvoteleft").html(response.data.left.nb_votes);
        $("#nbvotewinner").html(response.data.winner.nb_votes);
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
    var btnLine;
	$.getJSON('/all_unknown', {limit: limit}).done(function (response) {
		console.log("all_unknown received");
		$.each(response.data, function (idx, picture) {
            var facebook_id = picture.facebook_id;
			// console.log(idx);
			// console.log(picture.url);
			// console.log(facebook_id);
			if (idx % nb_per_line === 0) {
                container.append(line);
				container.append(btnLine);
                line = $(line_tmpl);
				btnLine = $(line_tmpl);
                btnLine.css('margin-bottom', '2em');
			}
			var imgdiv = $("<div />");
			imgdiv.attr('class', 'span' + 12/nb_per_line);
			var img = $("<img />");
            img.attr('status', 'unknown');
			img.attr('src', picture.url);
            img.attr('id', 'img_' + facebook_id);
			img.attr('facebook_id', facebook_id);
			var okButton = $("<button />");
            okButton.attr('class', 'span' + 12/nb_per_line/2);
			okButton.html("CONFIRMER");
			okButton.attr('action-type', 'confirm');
			okButton.attr('facebook_id', facebook_id);
            $(okButton).click(function () {
                console.log("clicked OK");
                var url = '/confirm_raw_picture';
                var img = $("img#img_"+facebook_id);
                img.attr('status', 'confirmed');
                var params = {'facebook_id': facebook_id}
                params['picture_width'] = img[0].naturalWidth;
                params['picture_height'] = img[0].naturalHeight;
                $.post(url, params).done(function (response){
                    console.log("confirmed picture "+ response.data.url);
                });
            });

			var badButton = $("<button />");
            badButton.attr('class', 'span' + 12/nb_per_line/2);
			badButton.html("SUPPRIMER");
			badButton.attr('action-type', 'delete');
			badButton.attr('facebook_id', facebook_id);
            $(badButton).click(function () {
                console.log("clicked badButton");
                var url = '/detach_raw_picture';
                $.post(url, {'facebook_ids': [facebook_id]}).done(function (response){
                    console.log("detached picture "+response);
                });
            });
			imgdiv.append(img);
			line.append(imgdiv);
            btnLine.append(okButton);
            btnLine.append(badButton);
		});
        var lastButtonLine = $(line_tmpl);
        var lastButton = $("<button />");
        lastButton.attr('class', 'span12');
        lastButton.html("SUPPRIMER TOUS");
        lastButton.attr('action-type', 'delete-all');
        $(lastButton).click(function () {
            console.log("clicked lastButton");
            var url = '/detach_raw_picture';
            var facebook_ids = [];
            $("img[status='unknown']").each(function (index, animg) {
                facebook_ids.push($(animg).attr('facebook_id'));
            });
            // console.log("facebook IDs: " + facebook_ids);
            $.post(url, {'facebook_ids': facebook_ids}).done(function (response){
                console.log("detached pictures "+ response);
                pageReload();
            });
        });
        lastButtonLine.append(lastButton);
        container.append(lastButtonLine);
	});
}


function startupLoadStep2() {

    console.log("startupLoadStep2");
    var container = $(".container");
    var line_tmpl = "<div class='row-fluid' />";

    $.getJSON('/picture_facing', function(response) {
        var facebook_id = response.data.picture.facebook_id;
        console.log(facebook_id);

        // line for image
        var imgline = $(line_tmpl);
        var imgdiv = $("<div />");
        imgdiv.attr('class', 'span12');
        var img = $("<img />");
        img.attr('src', response.data.picture.url);
        img.attr('id', 'img_' + facebook_id);
        imgdiv.append(img);
        imgline.append(imgdiv);
        container.append(imgline);

        var btnline = $(line_tmpl);
        var addButton = $("<button />");
        addButton.attr('class', 'span4');
        addButton.html("AJOUTER FACE");
        addButton.attr('action-type', 'add-face');
        addButton.attr('facebook_id', facebook_id);

        var doneButton = $("<button />");
        doneButton.attr('class', 'span4');
        doneButton.html("TERMINER");
        doneButton.attr('action-type', 'done');
        doneButton.attr('facebook_id', facebook_id);

        var badButton = $("<button />");
        badButton.attr('class', 'span4');
        badButton.html("SUPPRIMER PHOTO");
        badButton.attr('action-type', 'delete');
        badButton.attr('facebook_id', facebook_id);
        btnline.append(addButton);
        btnline.append(doneButton);
        btnline.append(badButton);
        container.append(btnline);

        var faceLine = $(line_tmpl);
        $.each(response.data.faces, function (idx, face) {
            var facediv = $("<div />");
            facediv.attr('class', 'span4');

            var faceimg = createFaceImg(face);

            var faceDelButton = $("<button />");
            faceDelButton.html("SUPPRIMER FACE");
            faceDelButton.attr('action-type', 'delete-face');
            faceDelButton.attr('picture_id', face.picture_id);

            facediv.append(faceimg);
            facediv.append(faceDelButton);
            faceLine.append(facediv);
        });
        container.append(faceLine);

        ias = $("img").imgAreaSelect({ aspectRatio: '1:1', handles: true, instance: true });

        $("button[action-type='add-face']").click(function () {
            var selection = ias.getSelection();
            var x = selection.x1;
            var y = selection.y1;
            var width = selection.x2 - selection.x1;
            var height = selection.y2 - selection.y1;
            console.log("Add Face !");
            console.log(x);
            console.log(y);
            console.log(width);
            console.log(height);
            $.post('/add_single_face', {facebook_id: facebook_id,
                                        face_x: x,
                                        face_y: y,
                                        face_width: width,
                                        face_height: height}).done(function (response) {
                console.log("Added face !!");
                console.log(response.data);
                pageReload();
            });
        });

        $("button[action-type='done']").click(function () {
            console.log("click done");
            $.post('/complete_raw_picture', {facebook_id: facebook_id}).done(function (response) {
                console.log("Completed raw picture !!");
                pageReload();
            });
        });

        $("button[action-type='delete']").click(function () {
            console.log("clicked badButton");
            var url = '/detach_raw_picture';
            $.post(url, {'facebook_ids': [facebook_id]}).done(function (response){
                console.log("detached picture "+response);
                pageReload();
            });
        });

        $("button[action-type='delete-face']").click(function () {
            console.log("clicked badButton face");
            var url = '/detach_face';
            var picture_id = $(this).attr('picture_id');

            $.post(url, {'picture_id': picture_id}).done(function (response){
                console.log("detached picture "+response);
                pageReload();
            });
        });
    });
}