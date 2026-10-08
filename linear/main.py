import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Google Apps Script 웹앱에서 요청할 수 있도록 Cross-Origin Resource Sharing(CORS)을 허용합니다.
CORS(app)

@app.route('/search', methods=['POST'])
def linear_search():
    """
    선형 검색(Linear Search)을 수행하고 각 단계별 과정을 기록하여 반환하는 API입니다.
    
    [Request JSON Body]
    - array: 검색 대상 리스트 (예: [12, 45, 7, 23, 56, 89, 34])
    - target: 찾고자 하는 값 (예: 56)
    
    [Response JSON]
    - target: 찾고자 하는 값
    - steps: 검색 과정의 각 단계를 담은 리스트
    - found: 검색 성공 여부 (True / False)
    - found_index: 찾은 위치 인덱스 (못 찾을 경우 -1)
    - total_steps: 총 비교 횟수
    - time_complexity: 시간 복잡도 정보
    - space_complexity: 공간 복잡도 정보
    """
    data = request.get_json()
    
    # 예외 처리: 데이터 유효성 검사
    if not data or 'array' not in data or 'target' not in data:
        return jsonify({'error': '유효한 array와 target 데이터를 제공해야 합니다.'}), 400
    
    try:
        arr = [int(x) for x in data['array']]
        target = int(data['target'])
    except ValueError:
        return jsonify({'error': '배열 요소와 target은 정수 형태이어야 합니다.'}), 400

    steps = []
    found = False
    found_index = -1
    
    # 선형 검색 알고리즘 수행 (O(N))
    for index, value in enumerate(arr):
        is_match = (value == target)
        
        # 각 단계별 기록 저장
        step_info = {
            'step': index + 1,          # 단계 번호 (1부터 시작)
            'current_index': index,      # 현재 검사 중인 인덱스
            'current_value': value,      # 현재 검사 중인 값
            'is_match': is_match,        # 타겟과 일치 여부
            'array_state': arr           # 현재 배열 상태
        }
        steps.append(step_info)
        
        # 타겟을 찾으면 검색 종료
        if is_match:
            found = True
            found_index = index
            break

    # 결과 응답 생성
    response = {
        'target': target,
        'steps': steps,
        'found': found,
        'found_index': found_index,
        'total_steps': len(steps),
        'time_complexity': {
            'best': 'O(1) - 첫 번째 요소가 타겟인 경우',
            'average': 'O(N) - 평균적으로 N/2번 비교',
            'worst': 'O(N) - 마지막에 있거나 요소가 없는 경우'
        },
        'space_complexity': 'O(1) - 추가적인 메모리 공간을 거진 사용하지 않음'
    }

    return jsonify(response), 200

# Cloud Run에서 주입하는 PORT 환경변수 사용 (기본값 8080)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
