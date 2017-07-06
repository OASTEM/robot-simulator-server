from flask import Flask, render_template, request
import container
import json

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run():
    code = request.data
    print("Running code.")
    run_id = container.run_code(code)
    print("Got run id {}, waiting...".format(run_id))
    container.wait(run_id)
    print("Getting output.")
    run_out = container.get_output(run_id)

    print("Removing.")
    container.remove(run_id)
    return json.dumps({"out": run_out, "dbg": "Run ID {}".format(run_id)})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
