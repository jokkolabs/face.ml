
var session_id = null;
var fb_user_id = '';
var ias;
var DEFAULT_FACE_SIZE = 200;
var tags = {};
var favorites = [];

function pageReload() {
    window.location.reload(true);
}

function is_in_favorites(face_id) {
    return (favorites.indexOf(face_id) != -1);
}

function getSpacer(mini) {
    var cls = "spacer";
    if (mini === true)
        cls = "minispacer";
    var spacer = $("<div />");
    spacer.attr('class', cls);
    return spacer;
}

function addToolTip(elem, title) {
    elem.attr('data-placement', "top");
    elem.attr('data-toggle', "tooltip");
    elem.attr('data-original-title', title);
    elem.tooltip();
}

function createFaceImg(picture, face_size) {
    if (face_size === null || face_size === undefined)
        face_size = DEFAULT_FACE_SIZE;
    var new_width = Math.floor(picture.source_width * face_size / picture.face_width);
    var new_height = Math.floor(picture.source_height * face_size / picture.face_height);
    var margin_left = -Math.floor(new_width * picture.face_x / picture.source_width);
    var margin_top = -Math.floor(new_height * picture.face_y / picture.source_height);

    var containerDiv = $("<div />");
    containerDiv.attr('face_id', picture.face_id);
    var tag = 'tag-' + picture.tag || 'NOTTAGGED';
    containerDiv.attr('class', 'facemaincontainer '+ tag);
    containerDiv.css('width', face_size + 20);
    containerDiv.css('height', face_size + 20);

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

    var btnDiv = $("<div />");
    btnDiv.attr('class', 'dropdown');

    var iconEnlarge = $("<i class='icon-fullscreen' rel='prettyPhoto'></i>");
    iconEnlarge.attr('href', picture.url);
    addToolTip(iconEnlarge, "Agrandir (voir la photo complète).");

    //class="btn btn-primary dropdown-toggle" data-toggle="dropdown"
    var iconTag = $("<i class='icon-tags dropdown-toggle'></i>");
    // iconTag.attr('title', "Attribuer un tag");
    addToolTip(iconTag, "Cliquez pour donner votre avis !");
    iconTag.attr('data-toggle', "dropdown");
    iconTag.attr('role', "button");
    var tagMenu = $("<ul />");
    tagMenu.attr('class', 'dropdown-menu');
    for (var tag_id in tags) {
        var tagItem = $("<li />");
        tagItem.attr('tag_id', tag_id);
        tagItem.attr('face_id', picture.face_id);
        var tagLink = $("<a />");
        tagLink.click(function(){
            var face_id = $(this).parent().attr('face_id');
            var tag_id = $(this).parent().attr('tag_id');
            console.log("Tagged PIC " + face_id + " with " + tag_id);
            // send post to tag pic
        });

        var textureSpan = $("<span />");
        textureSpan.attr('class', 'texture tag-' + tag_id);
        var nameSpan = $("<span />");
        nameSpan.html(tags[tag_id]);
        var numberSpan = $("<span />");
        numberSpan.html(4);

        tagLink.append(textureSpan);
        tagLink.append(numberSpan);
        tagLink.append(nameSpan);
        tagItem.append(tagLink);
        tagMenu.append(tagItem);
    }

    var iconScore = $("<i class='icon-thumbs-up'></i>");
    var titleScore = "Score";
    // iconScore.attr('title', titleScore);
    addToolTip(iconScore, titleScore);
    var textScore = $("<span />");
    textScore.attr('class', 'score-text');
    // textScore.attr('title', titleScore);
    addToolTip(textScore, titleScore);
    textScore.html(picture.score || 0);

    var iconViews = $("<i class='icon-eye-open'></i>");
    var titleViews = "Nombre de vues";
    // iconViews.attr('title', titleViews);
    addToolTip(iconViews, titleViews);
    var textViews = $("<span />");
    // textViews.attr('title', titleViews);
    addToolTip(textViews, titleViews);
    textViews.html(picture.views || 0);

    var iconFav = $("<i class='icon-star'></i>");
    // iconFav.attr('title', "Ajouter à vos favoris");
    addToolTip(iconFav, "Ajouter à vos favoris");
    $(iconFav).click(function(){
        console.log("FACE TO FAV: "+ picture.face_id);
        $.post('/add_to_fav', {'face_id': picture.face_id,
                               'session_id': session_id})
            .done(function(response){
                console.log(response);
                var btnDiv = $(this).parent;
                console.log(btnDiv);
                // btnDiv.append(getSpacer());
                // btnDiv.append(iconInFav);
           });
    });
    var textFav = $("<span />");
    // textFav.attr('title', "Nombre de personnes l'ayant en favoris");
    addToolTip(textFav, "Nombre de personnes l'ayant en favoris");
    textFav.html(picture.nb_favorited || 0);

    var iconInFav = $("<i class='icon-bookmark'></i>");
    // iconInFav.attr('title', "C'est un de vos favoris.");
    addToolTip(iconInFav, "C'est un de vos favoris.");

    btnDiv.append(getSpacer());
    btnDiv.append(iconEnlarge);
    btnDiv.append(getSpacer(true));
    btnDiv.append(getSpacer());
    btnDiv.append(iconTag);
    btnDiv.append(tagMenu);
    btnDiv.append(getSpacer());
    btnDiv.append(getSpacer(true));
    btnDiv.append(iconScore);
    btnDiv.append(textScore);
    btnDiv.append(getSpacer());
    btnDiv.append(iconViews);
    btnDiv.append(getSpacer(true));
    btnDiv.append(textViews);
    btnDiv.append(getSpacer());
    btnDiv.append(iconFav);
    btnDiv.append(getSpacer(true));
    btnDiv.append(textFav);
    if (is_in_favorites(picture.face_id) === true) {
        btnDiv.append(getSpacer());
        btnDiv.append(iconInFav);
    }

    containerDiv.append(imgDiv);
    containerDiv.append(btnDiv);

    return containerDiv;
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
	// request session ID
    $.get('/reg_anonymous').done(function (response){
        session_id = response.data.session_id;
        refresh();
    });
}


function facebook_login_callback(response) {
    if (response.authResponse) {
		console.log('Welcome!  Fetching your information.... ');
		var access_token = FB.getAuthResponse()['accessToken'];
		console.log('Access Token = '+ access_token);
		$.get('/fbget', {'token': access_token});

		FB.api('/me', function(response) {
			console.log('Good to see you, ' + response.first_name + '.');
			console.log(response);
			fb_user_id = response.id;
			$.post('/fbupdate', response).done(function (resp) {
				refresh();
			});
		});
	} else {
		console.log('User cancelled login or did not fully authorize.');
	}
}


function refresh() {
	$.get('/refresh', {'session_id': session_id}).done(function(response) {
		console.log("refreshed: " + response);
        $(response.data.favorites).each(function (idx, favorite) {
            favorites.push(favorite.face_id);
        });
        console.log(response.data);
        tags = response.data.all_tags;
        // $("#winner_pic").html(createFaceImg(response.data.winner, 250));
        $("#left_pic").html(createFaceImg(response.data.left));
        $("#right_pic").html(createFaceImg(response.data.right));
        // $("#nbvoteright").html(response.data.right.nb_votes);
        // $("#nbvoteleft").html(response.data.left.nb_votes);
        // $("#nbvotewinner").html(response.data.winner.nb_votes);
        $("i[rel^='prettyPhoto']").prettyPhoto({
            show_title: false,
            show_description: false,
            theme: 'light_square',
            modal: false,
            social_tools: '',
        });
	});
}


function setUpMainPageEvents() {
	console.log('setUpMainPageEvents');
	$(".fblogin").click(function () {
		FB.login(facebook_login_callback, {scope: 'read_stream'});
	});
}


function startupLoadStep1() {
	console.log("startupLoadStep1");
	var limit = 60;
	var nb_per_line = 6;
	var container = $(".container");
	var bin = $(".bin");
	var line_tmpl = "<div class='row-fluid' />";
	var line;
    var btnLine;
	$.getJSON('/all_unknown', {limit: limit}).done(function (response) {
		console.log("all_unknown received");
		$.each(response.data, function (idx, picture) {
            var facebook_id = picture.facebook_id;
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
			img.attr('src', picture.url_thumbnail);
			img.attr('origurl', picture.url);
            img.attr('id', 'img_' + facebook_id);
			img.attr('facebook_id', facebook_id);
			var okButton = $("<button />");
            okButton.attr('class', 'span' + 12/nb_per_line/2);
			okButton.html("CONF");
			okButton.attr('action-type', 'confirm');
			okButton.attr('facebook_id', facebook_id);
            $(okButton).click(function () {
                console.log("clicked OK");
                var url = '/confirm_raw_picture';
                var img = $("img#img_"+facebook_id);
                img.attr('status', 'confirmed');
                img.attr('class', "confirmed");
                var imgOrig = $("<img />");
                imgOrig.attr('class', 'notdisplayed');
                imgOrig.attr('src', img.attr('origurl'));
                // bin.append(imgOrig);
                imgOrig.load(function () {
					var params = {'facebook_id': facebook_id};
					params['picture_width'] = $(this)[0].naturalWidth;
					params['picture_height'] = $(this)[0].naturalHeight;
					$.post(url, params).done(function (response){
						console.log("confirmed picture "+ response.data.url);
					});
                });
            });

			var badButton = $("<button />");
            badButton.attr('class', 'span' + 12/nb_per_line/2);
			badButton.html("SUPP");
			badButton.attr('action-type', 'delete');
			badButton.attr('facebook_id', facebook_id);
            $(badButton).click(function () {
                console.log("clicked badButton");
                var url = '/detach_raw_picture';
                img.attr('class', "badpicture");
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
        console.log(response);
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
        addButton.attr('class', 'span3');
        addButton.html("AJOUTER FACE");
        addButton.attr('action-type', 'add-face');
        addButton.attr('facebook_id', facebook_id);

        var adddoneButton = $("<button />");
        adddoneButton.attr('class', 'span3');
        adddoneButton.html("AJOUTER ET TERMINER");
        adddoneButton.attr('action-type', 'add-done');
        adddoneButton.attr('facebook_id', facebook_id);

        var doneButton = $("<button />");
        doneButton.attr('class', 'span3');
        doneButton.html("TERMINER");
        doneButton.attr('action-type', 'done');
        doneButton.attr('facebook_id', facebook_id);

        var badButton = $("<button />");
        badButton.attr('class', 'span3');
        badButton.html("SUPPRIMER PHOTO");
        badButton.attr('action-type', 'delete');
        badButton.attr('facebook_id', facebook_id);
        btnline.append(addButton);
        btnline.append(doneButton);
        btnline.append(adddoneButton);
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

        $("button[action-type='add-done']").click(function () {
            console.log("click add and done");
            var selection = ias.getSelection();
            var width = selection.x2 - selection.x1;
            var height = selection.y2 - selection.y1;
            console.log("Add Face !");
            $.post('/add_single_face', {facebook_id: facebook_id,
                                        face_x: selection.x1,
                                        face_y: selection.y1,
                                        face_width: width,
                                        face_height: height}).done(function (response) {
            $.post('/complete_raw_picture', {facebook_id: facebook_id}).done(function (response) {
                console.log("Completed raw picture !!");
                pageReload();
            });
                console.log("Added face !!");
                console.log(response.data);
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
