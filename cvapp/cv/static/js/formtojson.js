// Deals with making JSON out of form data

function split( val ) {
	return val.split( /,\s*/ );
}

function extractLast( term ) {
	return split( term ).pop();
}
			
// This guy creates the JSON - It's pretty awesome (I didn't make this)
$.fn.serializeObject = function() {
	if ( !this.length ) { return false; }

	var $el = this,
	  data = {},
	  lookup = data; //current reference of data

	var tempobj = {};
	
	// Set of stuff that needs to be in given order.
	var order = "experience_workplaces_education_technology_other";
	  
	  $el.find(':input[type!="checkbox"][type!="radio"], input:checked').each(function() {
		// data[a][b] becomes [ data, a, b ]
		var named = this.name.replace(/\[([^\]]+)?\]/g, ',$1').split(','),
			cap = named.length - 1,
			i = 0;
		
		// If the current inputfield or textarea is one of the ordered items
		var orderindex = order.indexOf(named[0]);
		if ( orderindex >= 0 ) {
			
			// Assign the value to the object 
			tempobj[ named[cap] ] = getLegalValIfTextarea( $(this) );
			
			// If it's the last of a set, push the previous set and reset the temporary object container
                // techs is always last of set experience.
                // if it has orderindex > 0, it means it's not experience, so description is the last field. 
                // data is last for other and technology
			if( named[cap] == "techs" || (orderindex > 0 && named[cap] == "description") || named[cap] == "data" ) {
				// If the we don't have the given array in the data-container object, create it
				if( !data[named[0]] ) {
					data[named[0]] = [];
				}
				// Push and reset
				data[named[0]].push(tempobj);
				tempobj = {};
			}
			
		// Ensure that only elements with valid `name` properties will be serialized
		} else if ( named[ 0 ] ) {
		  for ( ; i < cap; i++ ) {
			  // move down the tree - create objects or array if necessary
			  lookup = lookup[ named[i] ] = lookup[ named[i] ] ||
				  ( named[i+1] == "" ? [] : {} );
		  }

		  // at the end, psuh or assign the value
		  if ( lookup.length != undefined ) {
			   lookup.push( getLegalValIfTextarea( $(this) ) );
		  } else {
				lookup[ named[ cap ] ] = getLegalValIfTextarea( $(this) );
		  }

		  // assign the reference back to root
		  lookup = data;

		}
	  });

	return data;
};

//Remove illegal characters from word
function getLegalValIfTextarea($t) {
    var word = $t.val();
    return word;
    /*
    if( $t[0].tagName == "TEXTAREA" && !$t.hasClass('h5') ) {
        word = word.replace(/&/g, "&amp;");
        console.log('textarea:');
        console.log(word);
    }
	// Remove double quotes and line breaks
	return word.replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/\n/g, "<br/>");
    */
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