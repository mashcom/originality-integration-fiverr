angular
  .module("Whatsapp", [])
  .directive("ngScrollBottom", [
    "$timeout",
    function ($timeout) {
      return {
        scope: { ngScrollBottom: "=" },
        link: function ($scope, $element) {
          $scope.$watchCollection("ngScrollBottom", function (newValue) {
            if (newValue) {
              $timeout(function () {
                $element.scrollTop($element[0].scrollHeight);
              }, 0);
            }
          });
        },
      };
    },
  ])
  .component("loadingMask", {
    templateUrl: "/backend/whatsapp/loading_mask.html",
  })
  .component("contactMask", {
    templateUrl: "/backend/whatsapp/load_contacts.html",
  })
  .controller("whatsappCtrl", [
    "$scope",
    "$rootScope",
    "$http",
    function ($scope, $rootScope, $http) {
      $scope.loading_ui = true;
      $scope.APP_BASE_URL = window.location.origin + "/admin/whatsapp/";
      $scope.API_BASE = $scope.APP_BASE_URL;
      $scope.loading_chats = true;
      $scope.loading_contacts = true;
      $http.defaults.headers.post["Content-Type"] =
        "application/x-www-form-urlencoded";
      var transform = function (data) {
        return $.param(data);
      };
      $scope.init_chat_app = function () {
        Pusher.logToConsole = true;
        var pusher_auth_key = angular.element(document.getElementById("pusher_auth_key")).val();
        alert($pusher_auth_key);
        var pusher = new Pusher("f78032fe1d25906f189c", { cluster: "ap2" });
        var channel = pusher.subscribe("my-channel");
        channel.bind("my-event", function (data) {
          var from = data.from;
          var message = data.message;
          const audio = new Audio("/backend/whatsapp/incoming_sound.ogg");
          audio.play();
          successMsg(from + "<br/>" + message);
          $scope.get_contacts(false);
          $scope.get_chats($scope.active_user, false);
        });
      };
      $scope.get_contacts = function (show_progress = true) {
        $scope.loading_contacts = show_progress;
        $http.get($scope.API_BASE + "contacts").then(
          function success(response) {
            console.log(response);
            $scope.contacts = response.data;
            if ($scope.active_user == undefined) {
              $scope.active_user = $scope.contacts[0]["contact_id"];
            }
            $scope.get_chats($scope.active_user, show_progress);
            $scope.loading_contacts = false;
          },
          function error() {
            $scope.loading_contacts = false;
            alert("Network Error!");
          }
        );
      };
      $scope.mark_as_read = function (contact_id) {
        $http.get($scope.API_BASE + "read/" + contact_id).then(
          function success(response) {
            console.log(response);
          },
          function error() {
            console.log(response);
          }
        );
      };
      $scope.get_chats = function (contact_id, show_progress = true) {
        $scope.loading_chats = show_progress;
        $http.get($scope.API_BASE + "contact_chats/" + contact_id).then(
          function success(response) {
            console.log(response);
            $scope.active_user = contact_id;
            $scope.active_chats = response.data;
            $scope.loading_chats = false;
            $scope.mark_as_read(contact_id);
          },
          function error() {
            $scope.loading_chats = false;
            alert("Network Error!");
          }
        );
      };
      $scope.send_message = function () {
        $scope.message_sending = true;
        $http({
          method: "POST",
          url: $scope.API_BASE + "send",
          data: {
            to: $scope.active_user,
            message: $scope.typed_chat_message,
            media_url: $scope.media_url,
            media_type: $scope.media_type,
          },
          transformRequest: transform,
        }).then(
          function success(response) {
            console.log(response);
            if (response.data.success == true) {
              $scope.typed_chat_message = "";
              $scope.get_chats($scope.active_user);
              angular.element("#upload-media").modal("hide");
              document.getElementById("file").value = null;
              $scope.caption = "";
              successMsg(response.data.message);
            } else {
              successMsg(response.data.message);
            }
            $scope.message_sending = false;
          },
          function error(e) {
            $scope.message_sending = false;
            console.log(e);
          }
        );
      };
      $scope.send_media = function () {
        $scope.message_sending = true;
        var jq = jQuery.noConflict();
        var caption = angular.element(document.getElementById("caption")).val();
        var file_data = angular
          .element(document.getElementById("file"))
          .prop("files")[0];
        if (typeof file_data == "undefined") {
          alert("Please select file to upload");
          $scope.message_sending = false;
          return;
        }
        try {
          var file_size = file_data.size / 1024 / 1024;
          if (file_size > 5) {
            var fsize = +(Math.round(file_size + "e+2") + "e-2");
            alert(
              "File size can not exceed 5MB. Size selected is " + fsize + "MB"
            );
            $scope.message_sending = false;
            return;
          }
        } catch (e) {
          $scope.message_sending = false;
        }
        var form_data = new FormData();
        form_data.append("caption", caption);
        form_data.append("file", file_data);
        console.log("Form Data");
        console.log(form_data);
        $scope.uploading = true;
        jq.post({
          url: $scope.API_BASE + "upload_media",
          dataType: "json",
          cache: false,
          contentType: false,
          processData: false,
          data: form_data,
          error: function (httpobject, b, c) {
            $scope.uploading = false;
            $scope.message_sending = false;
            var msg = httpobject.responseText;
            if (httpobject.readyState == 0) {
              erroMsg("Unable to connect to the server. Please try again");
            }
            console.log(httpobject);
          },
          success: function (res) {
            $scope.message_sending = false;
            $scope.uploading = false;
            console.log("Consoler Rs");
            console.log(res);
            if (res.success == true) {
              $scope.media_url =
                window.location.origin +
                "/uploads/whatsapp/" +
                res.upload_data.file_name;
              $scope.media_type = res.upload_data.file_type;
              $scope.typed_chat_message = caption;
              $scope.send_message();
            } else {
              erroMsg(res.error);
            }
            console.log(res);
          },
        });
      };
    },
  ]);
