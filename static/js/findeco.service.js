/** It's all Svens fault!!1!11 **********************************************************
 * Copyright (c) 2012 Justus Wingert, Klaus Greff, Maik Nauheim                         *
 *                                                                                      *
 * This file is part of Findeco.                                                        *
 *                                                                                      *
 * Findeco is free software; you can redistribute it and/or modify it under             *
 * the terms of the GNU General Public License as published by the Free Software        *
 * Foundation; either version 3 of the License, or (at your option) any later           *
 * version.                                                                             *
 *                                                                                      *
 * Findeco is distributed in the hope that it will be useful, but WITHOUT ANY           *
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A      *
 * PARTICULAR PURPOSE. See the GNU General Public License for more details.             *
 *                                                                                      *
 * You should have received a copy of the GNU General Public License along with         *
 * BasDeM. If not, see <http://www.gnu.org/licenses/>.                                  *
 ****************************************************************************************/

/****************************************************************************************
 * This Source Code Form is subject to the terms of the Mozilla Public                  *
 * License, v. 2.0. If a copy of the MPL was not distributed with this                  *
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.                             *
 ****************************************************************************************/

'use strict';
/* Services */


angular.module('FindecoService', ['ngResource'])
    .config(function ($httpProvider) {
        $httpProvider.defaults.transformRequest = function(data){
            if (data === undefined) {
                return data;
            }
            return $.param(data);
        };
        // using this https://github.com/angular/angular.js/commit/8155c3a29ea0eb14806913b8ac08ba7727e1969c
        // to rename X-XSRFToken to X-CSRFToken because Django expects it that way
        $httpProvider.defaults.xsrfHeaderName = "X-CSRFToken";
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
    })
    .factory('FindecoService', function ($resource, $http) {
        function addSuccessAndError(value, promise) {
            value.success = function(fn) {
                promise.success(fn);
                return value;
            };
            value.error = function(fn) {
                promise.error(fn);
                return value;
            };
        }

        function fillArray(array, attributes) {
            return function (data) {
                for (var i = 0; i < attributes.length; ++i) {
                    data = data[attributes[i]];
                }
                array.length = 0;
                angular.forEach(data, function(item) {
                    array.push(item);
                });
            }
        }

        return {
            login: function(username, password) {
                var userInfo = {};
                var promise = $http.post('/.json_login/', {username: username, password:password});
                promise.success(function (d) {
                    angular.copy(d.loginResponse, userInfo);
                });
                addSuccessAndError(userInfo, promise);
                return userInfo;
            },
            logout: function() {
                return $http.get('/.json_logout/');
            },

            loadUserSettings: function() {
                var userInfo = {};
                var promise = $http.get('.json_loadUserSettings');
                promise.success(function (d) {
                    angular.copy(d.loadUserSettingsResponse, userInfo);
                });
                addSuccessAndError(userInfo, promise);
                return userInfo;
            },

            loadMicroblogging: function(microblogList, path, type, id) {
                var pathComponents = ['/.json_loadMicroblogging'];
                if (id != undefined) {
                    pathComponents.push(id);
                }
                if (type == undefined) {
                    type = "older"
                }
                pathComponents.push(type);
                pathComponents.push(path);
                var url = pathComponents.join('/');
                var promise = $http.get(url).success(fillArray(microblogList, ['loadMicrobloggingResponse']));
                addSuccessAndError(microblogList, promise);
                return microblogList;
            },

            storeMicroblogPost: function(path, microblogText) {
                var pathComponents = ['/.json_storeMicroblogPost', path];
                var url = pathComponents.join('/');
                return $http.post(url, {microblogText: microblogText});
            },

            loadArgument: function(indexNodes, path) {
                var url = ['/.json_loadIndex', 'true', path].join('/');
                var promise = $http.get(url);
                promise.success(fillArray(indexNodes, ['loadIndexResponse']));
                addSuccessAndError(indexNodes, promise);
                return indexNodes;
            },

            loadText: function(paragraphList, path) {
                var url = ['/.json_loadText', path].join('/');
                var promise = $http.get(url);
                promise.success(fillArray(paragraphList, ['loadTextResponse', 'paragraphs']));
                addSuccessAndError(paragraphList, promise);
                return paragraphList;
            },

            loadIndex: function(indexNodes, path) {
                var url = ['/.json_loadIndex', path].join('/');
                var promise = $http.get(url);
                promise.success(fillArray(indexNodes, ['loadIndexResponse']));
                addSuccessAndError(indexNodes, promise);
                return indexNodes;
            },

            loadGraphData: function(graphData, path, graphType) {
                if (graphType == undefined) {
                    graphType = "full";
                }
                var url = ['/.json_loadGraphData', graphType, path].join('/');
                var promise = $http.get(url);

                promise.success(fillArray(graphData, ['loadGraphDataResponse', 'graphDataChildren']));
                return promise;
            }
        };

    });