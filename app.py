from flask import Flask, render_template, request, redirect, url_for, render_template_string

app = Flask(__name__, template_folder='.', static_folder='static')

@app.route('/')
def home():
    return render_template('journal-federal.html')

@app.route('/unicpro', methods=['GET', 'POST'])
def unicpro():
    PASSWORD = "14785200"  # Change this password as needed

    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            return render_template('unic_pro.html')
        else:
            return render_template_string('''
                <div style="background-color:#121212; color:red; padding:2rem; font-family:sans-serif;">
                    <h2>Wrong password!</h2>
                    <a href="/unicpro" style="color:#0a84ff;">Try again</a>
                </div>
            ''')

    return '''
        <form method="POST" style="background-color:#121212; padding:3rem; color:white; font-family:sans-serif;">
            <h2>🔒 UNIC PRO Login</h2>
            <input type="password" name="password" placeholder="Enter password" required style="padding:0.5rem; font-size:1rem;">
            <button type="submit" style="margin-left:10px; padding:0.5rem 1.2rem;">Enter</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)