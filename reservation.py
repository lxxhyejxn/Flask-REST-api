from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random
import time
from markupsafe import escape

app = Flask(__name__)

BLOCKED_STATION_ID = 999  # Example stationID that is not allowed

@app.route('/reserve', methods=['GET','POST'])
def reserve():
    if request.method == 'POST':
    # POST 요청 처리
        data = request.get_json()
        
        # Define a helper function to check types
        def check_type(key, expected_type, allow_none=False):
            value = data.get(key)
            if value is None:
                return allow_none
            else:
                return isinstance(value, expected_type)
        
        # Define required fields with their expected types
        required_fields_with_types  = {
            'requestID': str,
            'passengerID': int,
            'serviceType': int,
            'passengerCount': int,
            'wheelchairCount': int,
            'pickupStationID': int,
            'dropoffStationID': int,
            # 'pickupTimeRequest': str
        }

        
        # Check for missing required fields or incorrect data types
        errors = {}
        for key, expected_type in required_fields_with_types.items():
            if not check_type(key, expected_type, allow_none=(key == 'pickupTimeRequest')):
                errors[key] = 'Incorrect data type' if data.get(key) is not None else 'Missing required data'

        if errors:
            return jsonify({"errors": errors}), 400
        
        time_list = []
        if data.get('pickupStationID') == BLOCKED_STATION_ID or data.get('dropoffStationID') == BLOCKED_STATION_ID:
            # time_list remains empty, resulting in an empty pickup_info_list
            pass
        else:
            # Proceed with other checks and populate time_list as needed
            pickup_time_request = data.get('pickupTimeRequest')
            request_time = datetime.now() + timedelta(minutes=10)

            if pickup_time_request is None or not isinstance(pickup_time_request, int):
                # Default time list for immediate request
                time_list = [request_time]
            else:
                try:
                    hhmm = pickup_time_request
                    hour = hhmm // 100
                    minute = hhmm % 100

                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        request_time = request_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    else:
                        return jsonify({"error": "Invalid time format"}), 400

                    time_list = [
                        request_time - timedelta(minutes=10),
                        request_time,
                        request_time + timedelta(minutes=5)
                    ]

                except ValueError as e:
                    errors['pickupTimeRequest'] = str(e)
                    return jsonify({"errors": errors}), 400
                
                

        # Generate pickup info list
        pickup_info_list = [{
            "tempDispatchID": f"temp{random.randint(100,999)}",
            "vehicleID": f"v-{random.randint(100,999)}-{time_item.strftime('%H%M%S')}",
            "pickupTime": int(time_item.strftime('%H%M'))
        } for time_item in time_list]
        
        message_time = int(time.time())
        request_id = f"req-{random.randint(1000, 9999)}"
        
        passenger_id = data['passengerID']
        service_type = data['serviceType']
        passenger_count = data.get('passengerCount',0)
        wheelchair_count = data.get('wheelchairCount', 0)  # default to 0 if not provided
        pickup_station_id = data['pickupStationID']
        dropoff_station_id = data['dropoffStationID']

        # 최종 결과 반환
        result = {
            "messageTime": message_time,
            "requestID": request_id,
            "passengerID": passenger_id,
            "pickupStationID": pickup_station_id,
            "dropoffStationID": dropoff_station_id,
            "passenger_count" : passenger_count,
            "wheelchair_count" : wheelchair_count,
            "pickupInfoList": pickup_info_list
        }

        return jsonify(result), 200
    else:
        return jsonify({"message": "GET 요청은 이 엔드포인트에서 처리되지 않습니다."}), 405


@app.route('/confirm', methods=['POST'])
def confirm():
    data = request.get_json()

    # 필수 데이터 검증
    if not data or not all(key in data for key in ['messageTime','requestID', 'confirmID']):
        return jsonify({"error": "필수 데이터 누락"}), 400

    # 확인 정보 생성
    message_time = data.get('messageTime')
    request_id = data.get('requestID')
    confirm_id = data.get('confirmID')

    # 최종 결과 반환
    result = {
        "messageTime": message_time,
        "requestID": request_id,
        "confirmID": confirm_id,
    }

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0' , port=5000)

