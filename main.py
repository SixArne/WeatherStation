from flask import Flask, request, jsonify
import mongo
import schedule
import sense_utils
import time
import threading
import datetime


flask_handle = Flask(__name__)

def process_data(mongo_handle):
    data = collect_data()

    has_inserted = mongo_handle.insert_weather_data(data)

    invalid_color = [255, 0, 0]
    valid_color = [0, 255, 0]
    duration = 0.1

    if not has_inserted:
        sense_utils.flash_light(invalid_color, duration)
    else:
        sense_utils.flash_light(valid_color, duration)
        

def collect_data():
    sense = sense_utils.get_sense()
    temp = sense_utils.get_temperature_measurement()

    data = {
        "temperature": temp,
        "gyroscope": sense.get_gyroscope(),
        "accelerometer": sense.get_accelerometer(),
        "barometric_pressure": sense.get_pressure(),
        "humidity": sense.get_humidity(),
        "timestamp": datetime.datetime.now()
    }

    return data

@flask_handle.route("/")
def hello():
    return "Hello, World!"

@flask_handle.route('/daily-average', methods=['POST'])
def daily_average():
    try:
        data = request.get_json()
        timestamp_str = data.get('timestamp')
        if not timestamp_str:
            return jsonify({"error": "Timestamp is required"}), 400
        
        timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        average_temp = mongo_handle.get_daily_average_temp(timestamp)
        
        if average_temp is not None:
            return jsonify({"average_temperature": average_temp, "date": timestamp.date()}), 200
        else:
            return jsonify({"error": "No data available for this day"}), 404

    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_flask():
    flask_handle.run(host='0.0.0.0', port=5000)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    mongo_handle = mongo.MongoInterface()
    schedule.every(30).seconds.do(lambda: process_data(mongo_handle))

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    run_scheduler()