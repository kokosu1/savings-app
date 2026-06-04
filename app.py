from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
        supabase_url=os.environ.get('SUPABASE_URL', ''),
        supabase_key=os.environ.get('SUPABASE_KEY', '')
    )

if __name__ == '__main__':
    app.run(debug=True)
