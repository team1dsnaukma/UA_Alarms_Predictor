from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/update_forecast', methods=['POST'])
def update_forecast():
    # Assuming the script file is named forecast_script.py
    script_path = '/Users/katerynalaptieva/Desktop/tg/parse_tg.py'
    # Execute the script
    try:
        subprocess.run(['python', script_path], check=True)
        return jsonify({'message': 'Forecast updated successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
