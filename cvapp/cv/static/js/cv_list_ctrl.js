var AcsApp = angular.module('AcsApp', ['ui.slider']);

AcsApp.controller('SearchCtrl', function($scope, $q, $http) {

  $scope.persons = [ ];
  $scope.numFound = 0;

  $scope.showListView = false;

  $scope.facetFields = [];
  $scope.yearsOfExperience = {};
  $scope.searchParameters = {};

  $scope.hideFilter = false;

  $scope.sortSetting = 'name_exact asc';
  $scope.customFilter = {
    list: [
      {title:'completed',   status: '',  query:'fulljson:"completeness+percent+100"~1'},
      {title:'recent',      status: '',  query:'last_edited:[NOW-120DAYS TO NOW]'},
      {title:'inactive',      status: '-', query:'status_exact:inactive'}
    ],
    getQueryString: function() {
      var queryArray = [];
      for(var i=0; i<this.list.length; i++){
        var cf = this.list[i];
        if(cf.status.length>0) queryArray.push( cf.status + cf.query );
      }
      return queryArray.join(' ');
    }
  };

  $scope.hasMorePersons = false;

  var firstrun = true;
  var rows = 10;
  var start = 0;

  var canceler;
 
  $scope.searchAcs = function(options) {

    options = options || {};
    options.loadMore = options.loadMore || false;

    console.log('Searching ACS...');

    var q = $scope.searchQuery || '*';

    if (canceler) {
      console.log('Cancelling previous search');
      canceler.resolve('Cancelled because of new search.');
    } else {
      console.log('Nothing to cancel');
    }
    canceler = $q.defer();

    if (options.loadMore) {
      start += rows;
    } else {
      start = 0;
    }

    $http({
      method: 'JSONP',
      url: 'https://acssolr:acssolr@acsdev.altrancloud.com/solr/acs/select',
      timeout: canceler.promise,
      params: {
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
    }).success(function (data) {
      if(!options.loadMore) $scope.persons = [];
      if(firstrun) {
        $scope.facetFields = processFacetFields( data.facet_counts.facet_fields );
        firstrun = false;
      } else {
        $scope.updateFacetFields( data.facet_counts.facet_fields );
      }
      var docs = data.response.docs;
      if( docs.length>0 ) {
        for( var i=0; i<docs.length; i++ ) {
          var person = JSON.parse( docs[i].rendered );
          person.image = person.image.replace(/(.jpg|.png)/gi,'_scale_110x110.jpg');
          $scope.persons.push( person );
        }
      }
      $scope.numFound = data.response.numFound;
      $scope.hasMorePersons = $scope.numFound > $scope.persons.length;
    });

  };

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

  function processFacetFields(rawFacetFields) {
    var facetFields = {};
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
      } else {
        var facetField = {
          name: rawFacetField.replace('_exact',''),
          facets: {}
        };
        for (var i=0; i<rawFacetFields[rawFacetField].length; i+=2){
          facetField.facets[ rawFacetFields[rawFacetField][i] ] = {
            count: rawFacetFields[rawFacetField][i+1],
            checked: false
          };
        }
        facetFields[rawFacetField] = facetField;
      }
    }
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
    }
    for( var facetField in $scope.facetFields ){
      var checkedFacets = [];
      if($scope.facetFields[facetField].facets['null'].checked){
        $scope.searchParameters.fq = $scope.searchParameters.fq || [];
        $scope.searchParameters.fq.push( '-'+facetField+':[* TO *]' );
      } else {
        for ( var facet in  $scope.facetFields[facetField].facets ){
          if( $scope.facetFields[facetField].facets[facet].checked ) {
            checkedFacets.push('"'+facet+'"');
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

    console.log($scope.searchParameters);
  }

  $scope.isRecent = function (dateString) {
    var numberOfDays = 120;
    return ( new Date().getTime() - new Date(dateString).getTime() ) / (1000*60*60*24) > numberOfDays;
  }
 
});
