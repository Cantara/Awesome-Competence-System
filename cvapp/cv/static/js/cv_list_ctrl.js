var AcsApp = angular.module('AcsApp', ['ui.slider']);

AcsApp.controller('SearchCtrl', function($scope, $q, $http, $compile, Url) {

  $scope.urls = DJANGO_URLS || {};

  $scope.persons = [ ];
  $scope.numFound = 0;
  $scope.totalFound = 0;

  $scope.showListView = false;
  $scope.multi = {
    format: 'DOC',
    language: 'Native language',
    template: 'Default template',
    params: {
      format: [
        {value: 'doc', label: 'DOC', checked: true},
        {value: 'pdf', label: 'PDF'},
        {value: 'odt', label: 'ODT'}
      ],
      language: [
        {value: 'native', label: 'Native', checked: true},
        {value: 'en', label: 'English'}
      ],
      template: CV_TEMPLATES
    },
    update: function(pName, text){
      this[pName] = text;
      console.log(pName, this[pName], text);
    }
  };

  $scope.facetFields = [];
  $scope.yearsOfExperience = {};
  $scope.searchParameters = {};

  $scope.hideFilter = false;

  var defaultSortSetting = 'name_exact asc'
  
  $scope.sortSetting = defaultSortSetting;

  $scope.customFilter = {
    list: [
      {title:'completed',   defaultStatus: 'all',  status: 'all',  query:'fulljson:"completeness+percent+100"~1'},
      {title:'recent',      defaultStatus: 'all',  status: 'all',  query:'last_edited:[NOW-120DAYS TO NOW]'},
      {title:'inactive',    defaultStatus: '-', status: '-', query:'status_exact:inactive'}
    ],
    getQueryString: function() {
      var queryArray = [];
      for(var i=0; i<this.list.length; i++){
        var cf = this.list[i];
        if(cf.status!='all') queryArray.push( cf.status + cf.query );
      }
      return queryArray.join(' ');
    }
  };

  $scope.hasMorePersons = false;
  $scope.isLoading = false;

  var firstrun = true;
  var defaultRows = 42;
  var start = 0;
  var canceler;

  function getSolrParams() {
    var q = $scope.searchQuery || '*';
    var rows = $scope.showListView ? 100000 : defaultRows;
    return { 
      'json.wrf': 'JSON_CALLBACK',
      q: $scope.customFilter.getQueryString() + ' ' + q,
      wt:'json',
      rows: rows,
      start: start,
      sort: $scope.sortSetting,
      fl: 'rendered',
      fq: $scope.searchParameters.fq || '',
      facet: 'true',
      'facet.missing': 'on',
      'facet.field': [
        'location_exact', 
        'department_exact',
        'years_of_experience_exact'
        ]
    }
  }
 
  $scope.searchAcs = function(options) {

    options = options || {};
    options.loadMore = options.loadMore || false;

    console.log('Searching ACS...');

    if (canceler) {
      console.log('Cancelling previous search');
      canceler.resolve('Cancelled because of new search.');
    } else {
      console.log('Nothing to cancel');
    }
    canceler = $q.defer();

    if (options.loadMore) {
      $scope.isLoading = true;
      start = $scope.persons.length;
    } else {
      start = 0;
    }

    $http({
      method: 'JSONP',
      url: $scope.urls.solr,
      timeout: canceler.promise,
      params: getSolrParams()
    }).success(function (data, st, he, co, stT) {
      if(!options.loadMore) $scope.persons = [];
      if(firstrun) {
        firstrun = false;
        // Get parameters from URL
        var urlParams = Url.getParams();
        // Process the facetfields for consumption
        $scope.facetFields = processFacetFields( data.facet_counts.facet_fields, urlParams );
        $scope.updateAndSearchAcs();
        $scope.totalFound = data.response.numFound;
      } else {
        $scope.updateFacetFields( data.facet_counts.facet_fields );
      }
      var docs = data.response.docs;
      if( docs.length>0 ) {
        for( var i=0; i<docs.length; i++ ) {
          var person = JSON.parse( docs[i].rendered );
          person.image = person.image.replace(/(.jpg|.png)/gi,'_scale_110x110.jpg');
          person.index = i;
          $scope.persons.push( person );
        }
      }
      $scope.numFound = data.response.numFound;
      $scope.hasMorePersons = $scope.numFound > $scope.persons.length;
      console.log('Found:', $scope.numFound, 'Shown:', $scope.persons.length, 'Hasmore:', $scope.hasMorePersons);
      renderPersons();
      $scope.isLoading = false;
    });

  };

  var tableRender, personRender;

  function renderPersons(){
    var html = '';

    if(!tableRender || !personRender){
      doT.templateSettings = {
        evaluate:    /\<\%([\s\S]+?)\%\>/g,
        interpolate: /\<\%=([\s\S]+?)\%\>/g,
        encode:      /\<\%!([\s\S]+?)\%\>/g,
        use:         /\<\%#([\s\S]+?)\%\>/g,
        define:      /\<\%##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\%\>/g,
        conditional: /\<\%\?(\?)?\s*([\s\S]*?)\s*\%\>/g,
        iterate:     /\<\%~\s*(?:\%\>|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\%\>)/g,
        varname: 'p',
        strip: true,
        append: true,
        selfcontained: false
      };

      var tableTemplate = $('#tabletemplate').text().replace(/999999999/g,'<%=p.id%>').replace(/999888999/g,'<%=cv.id%>');
      tableRender = doT.template(tableTemplate);
      var personTemplate = $('#persontemplate').text().replace(/111000111/g,'<%=p.id%>').replace(/888888888/g,'<%=cv.id%>');
      personRender = doT.template(personTemplate);
    }

    var render = $scope.showListView ? tableRender : personRender;

    for(var i=0; i < $scope.persons.length; i++){
      html += render($scope.persons[i]);
    }
    html = $compile(html)($scope);
    if($scope.showListView){
      var $mr = $("#multiresults");
      $mr.children().slice(1).remove();
      $mr.append(html); 
    } else {
      $('#cardresults').html(html);
    }
  }

  $scope.loadMorePeople = function() {
    $scope.searchAcs({
      loadMore: true
    });
  }

  $scope.updateAndSearchAcs = function(facetField, facetname) {
    facetField = facetField || '';
    facetname = facetname || '';
    console.log('UPDATE:', facetField, facetname);
    updateSearchParameters(facetField, facetname);
    $scope.searchAcs();
  }

  $scope.searchAcs();

  function processFacetFields(rawFacetFields, urlParams) {
    var facetFields = {};
    urlParams = urlParams || {};
    for( var rawFacetField in rawFacetFields ){
      if(rawFacetField == 'years_of_experience_exact') {
        var yof = rawFacetFields[rawFacetField];
        var maxValue = 0;
        var curValue = 0;
        for (var j=0;j<yof.length;j+=2){
          curValue = parseInt(yof[j]);
          if( curValue > maxValue ) {
            maxValue = curValue;
          }
        }
        $scope.yearsOfExperience = {
          min: 0,
          max: maxValue,
          range: true,
          step: 1,
          stop: function (event, ui) { $scope.updateAndSearchAcs(); }
        };
        $scope.yearsOfExperienceValue = [0, maxValue];
        if(urlParams.y && urlParams.y.length == 2){
          var valA = urlParams.y[0]*1;
          var valB = urlParams.y[1]*1;
          var vals = ( valA > valB ) ? [valB,valA] : [valA,valB];
          $scope.yearsOfExperienceValue = vals;
        }
      } else {
        var facetFieldName = rawFacetField.replace('_exact',''); // E.g. department, location
        var facetField = {
          name: facetFieldName,
          facets: {}
        };
        var checkedFacets = urlParams[facetFieldName] || false;
        for (var i=0; i<rawFacetFields[rawFacetField].length; i+=2){
          var value = rawFacetFields[rawFacetField][i];
          var count = rawFacetFields[rawFacetField][i+1];
          var checked = false;
          if(checkedFacets){
            checked = (checkedFacets.indexOf(value)>=0);
          }
          facetField.facets[value] = {
            count: count,
            checked: checked
          };
        }
        facetFields[rawFacetField] = facetField;
      }
    }

    // Read customfilter URL-Params
    for(var x = $scope.customFilter.list.length-1; x>0; x--){
      var cf = $scope.customFilter.list[x];
      if(urlParams[cf.title]){
        $scope.customFilter.list[x].status = urlParams[cf.title][0];
      }
    }

    // Reading sorting URL-Params
    if(urlParams.s) $scope.sortSetting = urlParams.s[0];

    // Reading q URL-Params
    if(urlParams.q) $scope.searchQuery = urlParams.q[0];

    // Reading view URL-Params
    if(urlParams.view) $scope.showListView = true;

    return facetFields;
  }

  $scope.updateFacetFields = function(rawFacetFields){
    console.log('Updating facet fields');
    for( var facetField in $scope.facetFields ){
      for (var i=0; i<rawFacetFields[facetField].length; i+=2){
        if( rawFacetFields[facetField][i] !== null ) {
          $scope.facetFields[ facetField ]
          .facets[ rawFacetFields[facetField][i] ]
          .count = rawFacetFields[facetField][i+1]; 
        }
      }
    }
  }

  function updateSearchParameters(ff, fn) {

    console.log('Updating search parameters.');
    
    $scope.searchParameters = {};
    
    var params = [];

    // Create Q URL-Params
    if($scope.searchQuery) params.push('q='+$scope.searchQuery);

    // Create Sorting URL-Params
    if($scope.sortSetting != defaultSortSetting) params.push('s='+$scope.sortSetting);

    // Unchecks other parameters if NULL is selected
    // Unchecks NULL if other parameters is selected
    if(ff.length>0){
      if(fn=='null'){
        for ( var facet in  ff.facets ){
          if(facet!='null') ff.facets[facet].checked = false;
        }
      } else {
        ff.facets['null'].checked = false;
      }
      console.log('Facet uncheck place:', ff);
    }
    for( var facetField in $scope.facetFields ){
      var checkedFacets = [];
      var facetFieldName = $scope.facetFields[facetField].name;
      if($scope.facetFields[facetField].facets['null'].checked){
        $scope.searchParameters.fq = $scope.searchParameters.fq || [];
        $scope.searchParameters.fq.push( '-'+facetField+':[* TO *]' );
        params.push(facetFieldName+'=null');
      } else {
        for ( var facet in  $scope.facetFields[facetField].facets ){
          if( $scope.facetFields[facetField].facets[facet].checked ) {
            checkedFacets.push('"'+facet+'"');
            params.push(facetFieldName+'='+encodeURI(facet));
          }
        }
        if(checkedFacets.length > 0) {
          $scope.searchParameters.fq = $scope.searchParameters.fq || [];
          $scope.searchParameters.fq.push( facetField+':('+checkedFacets.join(' OR ')+')' );
        }
      }
    }
    // Years-filter-query
    $scope.searchParameters.fq = $scope.searchParameters.fq || [];
    $scope.searchParameters.fq.push( 'years_of_experience_exact:['+$scope.yearsOfExperienceValue.join(' TO ')+']' );

    // Create URL-Params for years_of_experience
    if($scope.yearsOfExperienceValue[0]>0 || $scope.yearsOfExperienceValue[1]<$scope.yearsOfExperience.max){
      params.push('y='+$scope.yearsOfExperienceValue[0]);
      params.push('y='+$scope.yearsOfExperienceValue[1]);
    }

    // Create Customfilter URL-Params
    for(var x = $scope.customFilter.list.length-1; x>=0; x--){
      var cf = $scope.customFilter.list[x];
      if(cf.status != cf.defaultStatus) params.push(cf.title+'='+cf.status);
    }

    // Create listview URL-Params
    if($scope.showListView) params.push('view=list');

    console.log($scope.searchParameters);

    Url.setParams(params.join('&'));
  }

  $scope.isRecent = function(dateString) {
    var numberOfDays = 120;
    return ( new Date().getTime() - new Date(dateString).getTime() ) / (1000*60*60*24) > numberOfDays;
  }

  $scope.getJson = function() {
    var sp = getSolrParams();
    var s = [];
    for(key in sp){
      if(sp[key] instanceof Array){
        for(var i = sp[key].length-1; i>=0; i--){
          s.push(key+'='+encodeURI(sp[key][i]));
        }
      } else {
        s.push(key+'='+encodeURI(sp[key]));
      }
    }
    window.open($scope.urls.solr+'?'+s.join('&'));
  }

  // Download Multiple CVs
  $scope.downloadMulti = function() {
    var cvids = document.forms['multicv']['cvid'];
    var cvchecked = false;
    if(typeof cvids.length !== 'undefined'){
      for(var i = 0; i<cvids.length; i++) {
        if(cvids[i].checked){
          cvchecked = true;
          break;
        }
      }
    } else {
      cvchecked = cvids.checked;
    }
    if(cvchecked){
      document.forms['multicv'].submit();
    } else {
      alert('Please select CVs from the list for downloading.');
    }
    return false;
  }

  // Copy consultant e-mails
  $(function(){
    ZeroClipboard.config( { swfPath: DJANGO_URLS.static+'flash/ZeroClipboard.swf' } );
    var client = new ZeroClipboard($("#emailCopyButton"));
    client.on( "ready", function( readyEvent ) {
      // alert( "ZeroClipboard SWF is ready!" );
      client.on( "aftercopy", function( event ) {
        var copied = event.data["text/plain"];
        if( copied ) {
          alert('Copied '+copied.split(';').length+' emails:\n\n'+copied);
        } else {
          alert('Please select persons from the list for copying.');
        }
      });
    });
  });
  
  $scope.hasFlash = FlashDetect.versionAtLeast(9);

  $scope.showSelectedEmails = function() {
    $scope.selectedEmailsVisible = !$scope.selectedEmailsVisible;
    $('#selectedemails').select(); 
  }

  $scope.updateSelectedEmails = function() {
    var m = [];
    for(var i=0; i<$scope.persons.length; i++) {
      if($scope.persons[i].isSelected) m.push($scope.persons[i].mail);
    }
    $scope.selectedEmails = m.join('; ');
    $('#selectedemails').select();
  }

});
