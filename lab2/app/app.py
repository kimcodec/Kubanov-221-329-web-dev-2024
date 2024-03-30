from flask import Flask, render_template, request, make_response

app = Flask(__name__)
application = app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/headers')
def headers():
    return render_template('requestInfo.html', header='Заголовки', data=request.headers)


@app.route('/cookies')
def cookies():
    response = make_response(
        render_template('requestInfo.html', header='cookies', data=request.cookies)
    )
    response.set_cookie("MAYBE BABY", "BEST GIRL")
    return response


@app.route('/url_params')
def url_params():
    return render_template('requestInfo.html', header='url_params', data=request.args)


@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')


@app.route('/phone', methods=['GET', 'POST'])
def phone():
    if request.method == 'GET':
        return render_template('phone.html')

    formatted_phone_number = phone_number = request.form.get('phone_number', '')
    symbols_to_replace = {'+', ' ', '(', ')', '-', '.'}
    phone_number = ''.join([char for char in phone_number if char not in symbols_to_replace])

    errors = []

    if not phone_number.isdigit():
        errors.append('В номере телефона встречаются недопустимые символы.')
    if len(phone_number) not in [10, 11]:
        errors.append('Неверное количество цифр.')

    if not errors:
        formatted_phone_number = '8-{}-{}-{}-{}'.format(
            phone_number[-10:-7], phone_number[-7:-4], phone_number[-4:-2], phone_number[-2:]
        )

    return render_template('phone.html', phone_number=formatted_phone_number, errors=errors)

if __name__ == '__main__':
    app.run(debug=True)