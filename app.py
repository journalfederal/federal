from flask import Flask, render_template

app = Flask(__name__, template_folder='.', static_folder='.')

@app.route('/')
def home():
    return render_template('journal-federal.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)