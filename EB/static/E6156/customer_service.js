(function() {
    'use strict';
    /*
    @CommentService
    */
    angular
        .module('CustomerApp')

    .factory('CustomerService', [
        '$http', '$window',
        function($http, $window) {

            console.log("Hello!")

            var version = "678";

            // This is also not a good way to do this anymore.
            var sStorage = $window.sessionStorage;

            var customer_service_base_url = "http://127.0.0.1:5033/api";

            return {
                get_version: function () {
                    return ("1234");
                },
                driveLogin: function (email, pw, register,lastname,firstname) {

                    return new Promise(function(resolve, reject) {
                        console.log("Driving login.");
                        var url
                        if(!register) {
                            url = customer_service_base_url + "/login";
                            console.log("email = " + email);
                            console.log("PW = " + pw);

                            var bd = {"email": email, "password": pw};
                        }
                        else
                        {
                            url = customer_service_base_url + "/registrations";
                            console.log("email = " + email);
                            console.log("PW = " + pw);

                            var bd = {"email": email, "password": pw,"last_name":lastname,"first_name":firstname};
                        }
                        $http.post(url, bd).success(
                            function (data, status, headers) {
                                var rsp = data;
                                var h = headers();
                                var result = data.data;
                                console.log("Data = " + JSON.stringify(result, null, 4));
                                console.log("Headers = " + JSON.stringify(h, null, 4))
                                console.log("RSP = " + JSON.stringify(rsp, null, 4))

                                var auth = h.authorization;
                                sStorage.setItem("token", auth);

                                // add etag by hao
                                var etag = h.etag;
                                sStorage.setItem("etag", etag);
                                /////////////////////

                                resolve("OK")
                            }).error(function (error) {
                                console.log("Error = " + JSON.stringify(error, null, 4));
                                reject("Error")
                            });
                    });
                },
                getCustomer: function (email) {
                    return new Promise(function(resolve, reject) {
                        var url = customer_service_base_url + "/user/" + email;
                        $http({
                        url:url,
                        headers:{
                            "Authorization":sStorage.getItem("token"),
                            "Etag":sStorage.getItem("etag")
                        },
                        method:"GET",
                    }).success(
                            function (data, status, headers) {
                                var rsp = data;
                                console.log("RSP = " + JSON.stringify(rsp, null, 4));
                                resolve(rsp)
                            }).error(function (error) {
                                console.log("Error = " + JSON.stringify(error, null, 4));
                                reject("Error")
                            });
                    });
                }
            }
        }
    ])
})();