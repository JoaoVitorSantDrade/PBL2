from flask import Flask, request
import paho.mqtt.client as mqtt

app = Flask(__name__)


@app.route('/api/hidrometro/', methods=['GET'])
def see_hidrometro():
    args = request.args
    args = args.to_dict()
    #pedir para a nuvem que pesquise tal ID do hidrometro
    if args.get("id") == "":
        pass
    else:
        return 'Não encontrado'


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)