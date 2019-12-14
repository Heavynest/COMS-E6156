//var app = angular.module("CustomerApp", []);

CustomerApp.controller("profileController", function($scope, $http, $location, $window) {

    console.log("Profile controller loaded.")

    var s3 = jQuery.LiveAddress({
        key: "18981749384552786",
        waitForStreet: true,
        debug: true,
        target: "US",
        placeholder: "Enter address",
        addresses: [{
            freeform: '#newaddress'
        }]
    });

    s3.on("AddressAccepted", function(event, data, previousHandler)
    {
        console.log("Boo Yah!")
        console.log(JSON.stringify(data.response, null,3))

    });

    $scope.placeholder = "Update and select a choice.";
    // $scope.address="hh"
    $scope.addressKinds = ['Home', 'Work', 'Mobile','Other'];
    $scope.akind="Subtype"
    $scope.telekind="Subtype"
    $scope.emailkind="Subtype"
    $scope.otherkind="Subtype"
    $scope.profileinfo=null
    getinfo(0);
    // console.log($scope.customerInfo)

    $scope.addressKind = function(idx) {
        console.log("Address kknk = " + $scope.addressKinds[idx]);
        $scope.akind=$scope.addressKinds[idx];
        console.log("Address = " + $scope.address);
    };

    $scope.teleKind = function(idx) {
        console.log("Address kknk = " + $scope.addressKinds[idx]);
        $scope.telekind=$scope.addressKinds[idx];
        console.log("Address = " + $scope.address);
    };

    $scope.emailKind = function(idx) {
        console.log("Address kknk = " + $scope.addressKinds[idx]);
        $scope.emailkind=$scope.addressKinds[idx];
        console.log("Address = " + $scope.address);
    };
    $scope.otherKind = function(idx) {
        console.log("Address kknk = " + $scope.addressKinds[idx]);
        $scope.otherkind=$scope.addressKinds[idx];
        console.log("Address = " + $scope.address);
    };

    baseUrl = "http://127.0.0.1:5033/api";

    $scope.updateAddress=function()
    {
        update("ADDRESS",$scope.akind,$scope.address);
        $http({
            url:"http://127.0.0.1:5033/api/profile",
            method:"GET",
            params:{"uid":$scope.customerInfo["id"]}
        }).success(
            function(data, status, headers){
                console.log(data);
                $scope.profileinfo=data
            }).error(function (error) {
                console.log("Error = " + JSON.stringify(error, null, 4));
                reject("Error")
            });

    };
    $scope.updateTelephone=function(){update("TELEPHONE",$scope.telekind,$scope.telephone)};
    $scope.updateEmail=function(){update("EMAIL",$scope.emailkind,$scope.email)};
    $scope.updateOther=function(){update("OTHER",$scope.otherkind,$scope.other)};

    function getinfo(){
        // var req={
        //     method:"GET",
        //     url:"127.0.0.1:5033/api/profile?uid=42879052-d95e-42dc-ae9f-32b8f7e126c6"
        // };
        // url="127.0.0.1:5033/api/profile?uid=42879052-d95e-42dc-ae9f-32b8f7e126c6";
        $http({
            url:"http://127.0.0.1:5033/api/profile",
            method:"GET",
            params:{"uid":$scope.customerInfo["id"]}
        }).success(
            function(data, status, headers){
                console.log(data);
                $scope.profileinfo=data
            }).error(function (error) {
                console.log("Error = " + JSON.stringify(error, null, 4));
                reject("Error")
            });
    }


     function update(e_type,e_subtype,e_value){
        var body={"element_type":e_type,"element_subtype":e_subtype,"element_value":e_value,"uid":$scope.customerInfo["id"]};

        sStorage= $window.sessionStorage;
        var req={
            method:"POST",
            url:baseUrl+"/profile",
            headers:{'Authorization':sStorage.getItem("token")},
            data:body
        };
        $http(req
        ).success(
            function (data, status, headers) {
                // var rsp = data;
                // var h = headers();
                // var result = data.data;
                // console.log("Data = " + JSON.stringify(result, null, 4));
                // console.log("Headers = " + JSON.stringify(h, null, 4))
                // console.log("RSP = " + JSON.stringify(rsp, null, 4))
                //
                // var auth = h.authorization;
                // sStorage.setItem("token", auth);
                getinfo();
                $scope.insertsuccess=true;
                $("#InsertModal").modal();
                console.log("Cool");
                resolve("OK");
                // setTimeout(function(){$scope.$apply();},1000)
                // $scope.$apply();
            }).error(function (error) {
                $scope.insertsuccess=false
                $("#InsertModal").modal();
                console.log("Error = " + JSON.stringify(error, null, 4));
                reject("Error")
            });
    }

});

