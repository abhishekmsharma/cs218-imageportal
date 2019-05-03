$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				username : $('#usernameInput').val(),
				password: $('#passwordInput').val()
			},
			type : 'POST',
			url : '/login'
		})
		.done(function(data) {

			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.success).show();
				$('#errorAlert').hide();
				window.location.replace("/login");
			}

		});

		event.preventDefault();

	});

});