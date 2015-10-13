from flask import Flask
app = Flask(__name__)

@app.route("/")
def main():
    return "Welcome!"

def parse_reflog():
    pass

if __name__ == "__main__":
    app.run()
