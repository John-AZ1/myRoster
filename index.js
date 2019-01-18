let shiftlist = document.getElementById('shiftlist')
let username = document.getElementById('username')
let password = document.getElementById('password')

function updateShifts(username, password) {
	console.log("Called")
	const request = new XMLHttpRequest();
	request.open('PUSH', '/api/getRosterHTML', true);
	request.setRequestHeader('Content-type', 'application/json');
	request.send('{"Username": "'+username+'", "Password": "'+password+'"}');
	request.onreadystatechange = e => {
		shiftlist.innerHTML = request.responseText
	}
}
document.getElementById("login").addEventListener('click', e => {
	let username = document.getElementById("username").value
	let password = document.getElementById("password").value
	updateShifts(username, password)
})
