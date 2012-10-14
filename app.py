import os
from flask import Flask, request, session, render_template, make_response

app = Flask(__name__)
app.debug = True
app.secret_key = 'Artoo says that the chances of survival are 725 to 1'


@app.route('/')
def dashboard():
	return ("I really don't see how that is going to help! "
		"Surrender is a perfectly acceptable alternative in "
		"extreme circumstances!")


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
