from flask import Flask

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Hello! Future home of the JCO Philanthropy Dashboard.'


if __name__ == '__main__':
    app.run()