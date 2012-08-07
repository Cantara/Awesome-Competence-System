// Declare available tags for Autocomplete
var techTags = [
	"ActionScript",
	"AppleScript",
	"Asp",
	"BASIC",
	"C",
	"C++",
	"Clojure",
	"COBOL",
	"ColdFusion",
	"Erlang",
	"Fortran",
	"Groovy",
	"Haskell",
	"Java",
	"JavaScript",
	"Lisp",
	"Perl",
	"PHP",
	"Python",
	"Ruby",
	"Scala",
	"Scheme"
];
	
//Adds checkboxes for all techs when document is ready.
$(document).ready(function() {
	addTech();
	addExp();
	addWork();
	addEdu();
	addOther();
	$("#cvlist").hide();
	$("#preview_frame").hide();
	$("#save_frame").hide();
	$("#clearcv").hide();
});

// Declare settings for JqueryUI sortable()
var sortSettings = {
		forcePlaceholderSize: true,
		placeholder: 'dragplaceholder',
		opacity: 0.7,
		axis: 'y'
	};

//Binding functions and making things sortable/draggable - Some are here, some are in the buttons or whatever, I'm not that consistent
$(function() {
	$('form').submit(function() {
		getCVJson();
	});
	$("#photo").change(function() {
		upPhoto();
		return false;
	});
	
	$( "#technologies" ).sortable(sortSettings).disableSelection();
	$( "#experience" ).sortable(sortSettings).disableSelection();
	$( "#workplaces" ).sortable(sortSettings).disableSelection();
	$( "#education" ).sortable(sortSettings).disableSelection();
	$( "#other" ).sortable(sortSettings).disableSelection();
	
});


	function split( val ) {
		return val.split( /,\s*/ );
	}
	function extractLast( term ) {
		return split( term ).pop();
	}

	function techAutocomplete() {
		
		$( ".techitem" )
			// don't navigate away from the field on tab when selecting an item
			.bind( "keydown", function( event ) {
				if ( event.keyCode === $.ui.keyCode.TAB &&
						$( this ).data( "autocomplete" ).menu.active ) {
					event.preventDefault();
				}
			})
			.autocomplete({
				minLength: 0,
				source: function( request, response ) {
					// delegate back to autocomplete, but extract the last term
					response( $.ui.autocomplete.filter(
						techTags, extractLast( request.term ) ) );
				},
				focus: function() {
					// prevent value inserted on focus
					return false;
				},
				select: function( event, ui ) {
					var terms = split( this.value );
					// remove the current input
					terms.pop();
					// add the selected item
					terms.push( ui.item.value );
					// add placeholder to get the comma-and-space at the end
					terms.push( "" );
					this.value = terms.join( ", " );
					return false;
				}
			});
	}
			
			
// This guy creates the JSON - It's pretty awesome (I didn't make this)
$.fn.serializeObject = function() {
	if ( !this.length ) { return false; }

	var $el = this,
	  data = {},
	  lookup = data; //current reference of data

	  $el.find(':input[type!="checkbox"][type!="radio"], input:checked').each(function() {
		// data[a][b] becomes [ data, a, b ]
		var named = this.name.replace(/\[([^\]]+)?\]/g, ',$1').split(','),
			cap = named.length - 1,
			i = 0;

		// Ensure that only elements with valid `name` properties will be serialized
		if ( named[ 0 ] ) {
		  for ( ; i < cap; i++ ) {
			  // move down the tree - create objects or array if necessary
			  lookup = lookup[ named[i] ] = lookup[ named[i] ] ||
				  ( named[i+1] == "" ? [] : {} );
		  }

		  // at the end, psuh or assign the value
		  if ( lookup.length != undefined ) {
			   lookup.push( legalInput( $(this).val() ) );
		  }else {
				lookup[ named[ cap ] ]  = legalInput( $(this).val() );
		  }

		  // assign the reference back to root
		  lookup = data;

		}
	  });

	return data;
};
		  
function getCVJson() {
	var CVJson = $('#cvform').serializeObject();
	$('#visjson').val(FormatJSON(CVJson));
	return CVJson;
}

//Updates the photo to show the URL
function upPhoto() {
	$("#photoshow").attr("src", $("#photo").val());
}

function addExp(title, title_en, company, company_en, techs, years, description, description_en) {
	if(!title){
		title 		= "";
		title_en	= "";
		company		= "";
		company_en 	= "";
		years 		= "";
		description 	= "";
		description_en 	= "";
	}
		techs	 	= techs || "";
	var num = ++document.counters.expcount.value;
	var expBlock =
		'<fieldset>' +
			'<span class="x floatright" onClick="removeParent(this);" tabindex="1000">x</span>' + "\n" +
			'<div class="left">' + "\n" +
				'<label for="experience['+num+'][title]">		Jobbtittel</label> 					<input type="text" name="experience['+num+'][title]" 		id="experience['+num+'][title]" 		value="'+title 		+'"><br>' + "\n" +
				'<label for="experience['+num+'][title_en]">	Jobbtittel (ENG)</label>			<input type="text" name="experience['+num+'][title_en]" 	id="experience['+num+'][title_en]" 		value="'+title_en	+'"><br>' + "\n" +
				'<label for="experience['+num+'][company]">		Bedrift, prosjekt</label>			<input type="text" name="experience['+num+'][company]" 		id="experience['+num+'][company]" 		value="'+company	+'"><br>' + "\n" +
				'<label for="experience['+num+'][company_en]">	Bedrift, prosjekt (ENG)</label>		<input type="text" name="experience['+num+'][company_en]" 	id="experience['+num+'][company_en]" 	value="'+company_en +'"><br>' + "\n" +
				'<label for="experience['+num+'][techs]">	Teknologier</label>		<input type="text" name="experience['+num+'][techs]" 	id="experience['+num+'][techs]" 	value="'+techs +'" class="techitem"><br>' + "\n" +
				'<label for="experience['+num+'][years]">		Årstall</label>						<input type="text" name="experience['+num+'][years]" 		id="experience['+num+'][years]" 		value="'+years 		+'"><br>' +  "\n" +
			'</div>' + "\n" +
			'<div class="right">' + "\n" +
				'<label for="experience['+num+'][description]">Beskrivelse</label><br><textarea name="experience['+num+'][description]" id="experience['+num+'][description]" cols="30" rows="5">'+description+'</textarea><br>' + "\n" +
			'</div>' + "\n" +
			'<div class="right">' + "\n" +
				'<label for="experience['+num+'][description_en]">Beskrivelse (ENG)</label><br><textarea name="experience['+num+'][description_en]" id="experience['+num+'][description_en]" cols="30" rows="5">'+description_en+'</textarea><br>' + "\n" +
			'</div>' + "\n" +
		'</fieldset>' + "\n";
	$("#experience").append(expBlock);
	techAutocomplete();
}

function addWork(title, company, years, title_en, company_en) {
	if(!title){
		title 		= "";
		company		= "";
		years 		= "";
		title_en 	= "";
		company_en 	= "";
	}
	var num = ++document.counters.workcount.value;
	var workBlock =
		'<fieldset>' +
			'<span class="x floatright" onClick="removeParent(this);" tabindex="1000">x</span>' + "\n" +
			'<div class="left">' + "\n" +
			'<label for="workplaces['+num+'][title]">		Jobbtittel 			</label><input type="text" name="workplaces['+num+'][title]" 		id="workplaces['+num+'][title]" 		value="'+title	+'"><br>' + "\n" +
			'<label for="workplaces['+num+'][company]">		Bedrift 			</label><input type="text" name="workplaces['+num+'][company]" 		id="workplaces['+num+'][company]" 		value="'+company+'"><br>' + "\n" +
			'<label for="workplaces['+num+'][years]">		Årstall 			</label><input type="text" name="workplaces['+num+'][years]" 		id="workplaces['+num+'][years]" 		value="'+years	+'"><br>' + "\n" +
			'</div>' + "\n" +                                                                                                                                                                      
			'<div class="left">' + "\n" +                                                                                                                                                          
			'<label for="workplaces['+num+'][title_en]">	Jobbtittel (ENG) 	</label><input type="text" name="workplaces['+num+'][title_en]" 	id="workplaces['+num+'][title_en]" 		value="'+title_en	+'"><br>' + "\n" +
			'<label for="workplaces['+num+'][company_en]">	Bedrift (ENG) 		</label><input type="text" name="workplaces['+num+'][company_en]" 	id="workplaces['+num+'][company_en]" 	value="'+company_en	+'"><br>' + "\n" +
			'</div>' + "\n" +
		'</fieldset>' + "\n";
	$("#workplaces").append(workBlock);
}

function addEdu(title, school, years, title_en, school_en) {
	if(!title){
		title 		= "";
		school 		= "";
		years 		= "";
		title_en 	= "";
		school_en 	= "";
	}
	var num = ++document.counters.educount.value;
	var eduBlock =
		'<fieldset>' +
			'<span class="x floatright" onClick="removeParent(this);" tabindex="1000">x</span>' + "\n" +
			'<div class="left">' + "\n" +
			'<label for="education['+num+'][title]">		Utdanning			</label><input type="text" name="education['+num+'][title]" 		id="education['+num+'][title]" 		value="'+title+'"><br>' + "\n" +
			'<label for="education['+num+'][school]">		Studiested 			</label><input type="text" name="education['+num+'][school]" 		id="education['+num+'][school]" 	value="'+school+'"><br>' + "\n" +
			'<label for="education['+num+'][years]">		Årstall 			</label><input type="text" name="education['+num+'][years]" 		id="education['+num+'][years]" 		value="'+years+'"><br>' + "\n" +
			'</div>' + "\n" +
			'<div class="left">' + "\n" +
			'<label for="education['+num+'][title_en]">		Utdanning (ENG) 	</label><input type="text" name="education['+num+'][title_en]" 		id="education['+num+'][title_en]" 	value="'+title_en+'"><br>' + "\n" +
			'<label for="education['+num+'][school_en]">	Studiested (ENG) 	</label><input type="text" name="education['+num+'][school_en]" 	id="education['+num+'][school_en]" 	value="'+school_en+'"><br>' + "\n" +
			'</div>' + "\n" +
		'</fieldset>' + "\n";
	$("#education").append(eduBlock);
}

function addOther(title, title_en, data, data_en) {
	title = title || "";
	title_en = title_en || "";
	var num = ++document.counters.othercount.value;
	var otherBlock =
		'<fieldset>' +
			'<span class="x floatright" onClick="removeParent(this);" tabindex="1000">x</span>' + "\n" +
			'<div class="left">' + "\n" +
				'<label for="other['+num+'][title]">Emne</label><input type="text" name="other['+num+'][title]" id="other['+num+'][title]" value="'+title+'"><br>' + "\n" +
				'<label for="other['+num+'][title_en]">Emne (ENG)</label><input type="text" name="other['+num+'][title_en]" id="other['+num+'][title_en]" value="'+title_en+'"><br>' + "\n" +
			'</div>' + "\n" +
			'<div style="float:left;"><div class="right"><label>Norsk</label><div id="other'+num+'"></div>' + "\n" +
				'<input type="button" onClick="addOtherData('+num+');" value="+ Legg til felt" />' + "\n" +
			'</div>' + "\n" +
			'<div class="right"><label>Engelsk</label><div id="other'+num+'_en"></div>' + "\n" +
				'<input type="button" onClick="addOtherData('+num+',\'\',\'en\');" value="+ Legg til engelsk felt" />' + "\n" +
			'</div></div>' + "\n" +
		'</fieldset>' + "\n";
	$("#other").append(otherBlock);
	
	if(!data) {
		addOtherData(num);
	} else {
		for(d in data) {
			addOtherData(num,data[d]);
		}
	}
	if(!data_en) {
		addOtherData(num,"","en");
	} else {
		for(d in data) {
			addOtherData(num,data_en[d],"en");
		}
	}
}

function addOtherData(n,d,e) {
	var d = d || "";
	(e) ? e = "_en" : e = "";
	var dataBlock = '<span><input type="text" class="otheritem" name="other['+n+'][data'+e+'][]" value="'+d+'"><span class="x" onClick="removeParent(this);" tabindex="1000">x</span><br></span>' + "\n";
	$("#other"+n+e).append(dataBlock);
}

function addTech(title, title_en, data) {
	title = title || "";
	title_en = title_en || "";
	data = data || "";
	var num = ++document.counters.techcount.value;
	var techBlock =
		'<fieldset>' +
			'<span class="x floatright" onClick="removeParent(this);" tabindex="1000">x</span>' + "\n" +
			'<div class="left">' + "\n" +
				'<label for="technologies['+num+'][title]">Type</label><input type="text" name="technologies['+num+'][title]" id="technologies['+num+'][title]" value="'+title+'"><br>' + "\n" +
				'<label for="technologies['+num+'][title_en]">Type (ENG)</label><input type="text" name="technologies['+num+'][title_en]" id="technologies['+num+'][title_en]" value="'+title_en+'"><br>' + "\n" +
			'</div>' + "\n" +
			'<div class="right">' + "\n" +
				'<label for="technologies['+num+'][data]">List teknologier, separer med komma</label><br><textarea class="techitem" name="technologies['+num+'][data]" id="technologies['+num+'][data]" cols="30" rows="5">'+data+'</textarea><br>' + "\n" +
			'</div>' + "\n" +
		'</fieldset>' + "\n";
	$("#technologies").append(techBlock);
	
	/*$(".techitem").autocomplete({
		source: techTags,
		position: { my : "right top", at: "right bottom"}
	});*/
	
	techAutocomplete();
	
}

var techlist = {"Språk": ["Java","C/C++","Javascript","PHP","Basic","QBasic","Visual Basic"],
"Verktøy": ["Eclipse","Maven","Subversion","Git","Hudson","Nexus","Jira","Confluence","Fitnesse"]};

function addTechOld() {
	var techBlock = "";
	for(t in techlist) {
		techBlock = techBlock + "<fieldset><h4>" + t + "</h4>\n<ul>\n";
		for(ti in techlist[t]) {
			realT = techlist[t][ti];
			legalT = legalize(realT);
			techBlock = techBlock + '<li><input type="checkbox" name="technologies['+t+'][]" value="'+realT+'" id="'+legalT+'"> <label for="'+legalT+'">'+realT+'</label></li>'+"\n";
		}
		techBlock = techBlock + "</ul>\n</fieldset>\n";
	}
	$("#technologies").append(techBlock);
}

//Remove illegal characters from word
function legalize(word) {
	return word.replace(/[^a-zæøåöä0-9\-_:\.]|^[^a-z]+/gi, "_");
}

// Renser input-felt for rare verdier, så man får god JSON
function legalInput(w) {
	return w.replace(/[^a-zæøåöä0-9\-_:\.\+#()\\&;, /]/gi, "");
}

//Set a list of IDs to be checked or unchecked
function checkTech(list, checkedstate) {
	for(t in list) {
		for(ti in list[t]) {
			realT = list[t][ti];
			legalT = legalize(realT);
			$("#"+legalT).attr('checked', checkedstate);
		}
	}
}

function openCVList() {
	$('#preview_frame').hide();
	$('#save_frame').hide();
	$("#clearcv").hide();
	$('#cvlist').toggle(200);
}

function openClearCV() {
	$('#preview_frame').hide();
	$('#save_frame').hide();
	$("#clearcv").toggle(200);
	$('#cvlist').hide();
}

function loadCV(cvurl) {
	
	// Hvis cv lastes inn fra en gitt URL, mao det finnes ikke ulagret info, så skal vi ikke spørre om ting overskrives
	var confirmed = (cvurl) ? true : confirm("Er du sikker? Eksisterende informasjon vil bli slettet!");
	
	if($("#cvname").val() || cvurl) {
		cvurl = cvurl || $("#cvname").val();
	} else {
		return;
	}
	if(confirmed) {
		$.getJSON("cv/"+cvurl, function(c) {
			
			clearCV();
			
			var f = document.cvform;
			f.name.value 		= c.name;
			f.title.value 		= c.title;
			f.title_en.value 	= c.title_en || "";
			f.phone.value 		= c.phone;
			f.mail.value 		= c.mail;
			f.title_en.value 	= c.title_en || "";
			f.profile.value 	= c.profile;
			f.profile_en.value 	= c.profile_en || "";
			f.photo.value 		= c.photo;
			upPhoto();
			
			/* I liked these functions, but we're not gonna use them anymore :(
			//Uncheck all techs
			checkTech(techlist, false);
			//Check all items in list
			checkTech(c.technologies, true);
			*/
			
			for(x in c.technologies) {
				var e = c.technologies;
				addTech(e[x].title, e[x].title_en, e[x].data);
			}
			
			for(x in c.experience) {
				var e = c.experience;
				addExp(e[x].title, e[x].title_en || "", e[x].company, e[x].company_en || "", e[x].techs, e[x].years, e[x].description, e[x].description_en || "");
			}
			
			for(x in c.workplaces) {
				var e = c.workplaces;
				addWork(e[x].title, e[x].company, e[x].years, e[x].title_en || "", e[x].company_en || "");
			}
			
			for(x in c.education) {
				var e = c.education;
				addEdu(e[x].title, e[x].school, e[x].years, e[x].title_en || "", e[x].school_en || "");
			}
			
			for(x in c.other) {
				var e = c.other;
				addOther(e[x].title, e[x].title_en, e[x].data, e[x].data_en);
			}
			
		});
		$("#cvlist").hide(100);
	} else { 
		return; 
	}
}

function clearCV() {
	//Remove items, reset counters
	$("#technologies").empty();
	$("#experience").empty();
	$("#workplaces").empty();
	$("#education").empty();
	$("#other").empty();
	$("#techcount").val(0);
	$("#expcount").val(0);
	$("#workcount").val(0);
	$("#educount").val(0);
	$("#othercount").val(0);
	//Generic form reset
	document.cvform.reset();
}

function saveCV() {
	$('#preview_frame').hide();
	$("#clearcv").hide();
	$("#cvlist").hide();
	// If not visible, update then show
	if(!$('#save_frame').is(":visible")) {
		
		// Make sure the form target and action are correct
		document.showform.action = "savecv.php";
		document.showform.target = "save_frame";
		
		getCVJson();
		
		// Get filename from form data
		document.showform.cvfilename.value = legalize($("#name").val());
		//alert(document.showform.cvfilename.value);
		
		// Submit to save;
		document.showform.submit();
		
	}
	$('#save_frame').toggle(200);
	
}

function preview() {
	$('#save_frame').hide();
	$("#clearcv").hide();
	$("#cvlist").hide();
	// If not visible, update then show
	if(!$('#preview_frame').is(":visible")) {
		
		// Make sure the form target and action are correct
		document.showform.action = "cv.php";
		document.showform.target = "preview_framez";
		
		getCVJson();
		$("#showform").submit();
		
	}
	$('#preview_frame').toggle(200);
	
}

function closePopups() {
	$('#preview_frame').hide();
	$('#save_frame').hide();
	$("#cvlist").hide();
}

// Toggles group of information (e.g. Experience, Workplaces etc)
function toggleThis(t) {
	$(t).prev().toggleClass('closed');
	$(t).toggle("blind", 200);
}

// Delete an item (delete the parent)
function removeParent(t) {
	if(confirm("Er du sikker på at du vil slette?")) $(t).parent().remove();
}


function previewJson() {
	getCVJson();
}

// Formats the JSON to be more readable - http://joncom.be/code/javascript-json-formatter/
function FormatJSON(oData, sIndent) {
    if (arguments.length < 2) {
        var sIndent = "";
    }
    var sIndentStyle = "    ";
    var sDataType = RealTypeOf(oData);

    // open object
    if (sDataType == "array") {
        if (oData.length == 0) {
            return "[]";
        }
        var sHTML = "[";
    } else {
        var iCount = 0;
        $.each(oData, function() {
            iCount++;
            return;
        });
        if (iCount == 0) { // object is empty
            return "{}";
        }
        var sHTML = "{";
    }

    // loop through items
    var iCount = 0;
    $.each(oData, function(sKey, vValue) {
        if (iCount > 0) {
            sHTML += ",";
        }
        if (sDataType == "array") {
            sHTML += ("\n" + sIndent + sIndentStyle);
        } else {
            sHTML += ("\n" + sIndent + sIndentStyle + "\"" + sKey + "\"" + ": ");
        }

        // display relevant data type
        switch (RealTypeOf(vValue)) {
            case "array":
            case "object":
                sHTML += FormatJSON(vValue, (sIndent + sIndentStyle));
                break;
            case "boolean":
            case "number":
                sHTML += vValue.toString();
                break;
            case "null":
                sHTML += "null";
                break;
            case "string":
                sHTML += ("\"" + vValue + "\"");
                break;
            default:
                sHTML += ("TYPEOF: " + typeof(vValue));
        }

        // loop
        iCount++;
    });

    // close object
    if (sDataType == "array") {
        sHTML += ("\n" + sIndent + "]");
    } else {
        sHTML += ("\n" + sIndent + "}");
    }

    // return
    return sHTML;
}

// Formats the JSON to be more readable - http://joncom.be/code/javascript-json-formatter/
function RealTypeOf(v) {
  if (typeof(v) == "object") {
    if (v === null) return "null";
    if (v.constructor == (new Array).constructor) return "array";
    if (v.constructor == (new Date).constructor) return "date";
    if (v.constructor == (new RegExp).constructor) return "regex";
    return "object";
  }
  return typeof(v);
}