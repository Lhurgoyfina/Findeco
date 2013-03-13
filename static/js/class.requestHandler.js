/** ************************************************************************************
 * Copyright (c) 2013 Maik Nauheim findeco@maik-nauheim.de                        *
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
 * Findeco. If not, see <http://www.gnu.org/licenses/>.                                 *
 ****************************************************************************************/
 
/****************************************************************************************
 * This Source Code Form is subject to the terms of the Mozilla Public                  *
 * License, v. 2.0. If a copy of the MPL was not distributed with this                  *
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.                             *
 ****************************************************************************************/





function ClassRequestHandler() {}
var RqHandler = new ClassRequestHandler();
ClassRequestHandler.prototype.count =0;
ClassRequestHandler.prototype.post = function (e) {
    // Blocking the UI on post requests as default 
    if (typeof e.blocking ==  'undefined'){
        e.blocking = true;
    }
    if (e.blocking == true){ 
        this.block();
    }
    e.callback = e.success;
    e.type = 'POST';    
    e.dataType = 'json';
    e.beforeSend = function(xhr, settings) { xhr.setRequestHeader("X-CSRFToken", Helper.getCSRFToken()); }
    e.success = function(data) { RqHandler.callback(data, this); }
    e.error = RqHandler.httpErrorCheck;
    $.ajax(e)   ;
    
}

ClassRequestHandler.prototype.get  = function (e) {
    if (typeof e.blocking ==  'undefined'){
        e.blocking = false;
    }
    if (e.blocking == true){ 
        this.block();
    }
    e.callback = e.success;
    e.type = 'GET';    
    e.dataType = 'json';
    e.beforeSend = function(xhr, settings) { xhr.setRequestHeader("X-CSRFToken", Helper.getCSRFToken()); }
    e.success = function(data) { RqHandler.callback(data, this); }        
    e.error = RqHandler.httpErrorCheck;
    $.ajax(e);
}

ClassRequestHandler.prototype.callback = function (data, event) {
    if (event.blocking == true){ 
        this.count=this.count-1;
        this.unblock();
    }
    if ( typeof data['errorResponse'] !=  'undefined' ) {
        var inserts = data['errorResponse']['additionalInfo'];
        var text = Language.get(data['errorResponse']['errorID']); 
        alert(text.format(inserts));
        return false;
    }
    if ( event.callback == 'none' ){
        return false;
    }
    
    if ( typeof event.callback != 'undefined' ){ 
        event.callback(data, event);
    } else {
        for ( var SuccessID in data ) {
           alert(Language.get(SuccessID +'Success'));
           break; // or do something with it and break
        }
    }
}

ClassRequestHandler.prototype.httpErrorCheck = function (xhr, textStatus, errorThrown) {
    // Unblock on Error
    this.count=0;
    this.unblock();
        
    switch (xhr.status) {
        case 404:
            alert(Language.get('httpProposalNotFound'));
        break;
        case 500:
            alert(Language.get('httpInternalServerError'));
        break;
        default:
            alert(Language.get('httpUnhandledResponse /n') + textStatus + ' ' + errorThrown);
        break;
    }
}

ClassRequestHandler.prototype.block = function () {
    this.count=this.count+1;
    $('#loading').show();
    
}

ClassRequestHandler.prototype.unblock = function () {
    if (this.count==0){
        $('#loading').hide();
    }
}








