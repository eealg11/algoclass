"""
main.py
Google Cloud Run 배포를 위한 FastAPI 백엔드 서버 (Heap Sort & Counting Sort Dual Visualizer)
"""

import os
import random
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models import SortRequest, DualSortResponse
from algorithms import run_heap_sort, run_counting_sort

# 1. FastAPI 애플리케이션 초기화
app = FastAPI(
    title="Dual Sort Visualization Backend API",
    description="힙 정렬(Heap Sort)과 도수 정렬(Counting Sort)의 단계별 스냅샷 데이터를 제공하는 Cloud Run 백엔드",
    version="1.0.0"
)

# 2. CORS(Cross-Origin Resource Sharing) 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="루트 헬스체크")
@app.get("/health", summary="Cloud Run 컨테이너 헬스체크")
def health_check():
    """
    Google Cloud Run 배포 및 인프라 모니터링을 위한 헬스체크 엔드포인트
    """
    return {
        "status": "healthy",
        "service": "dual-sort-visualization-server",
        "version": "1.0.0",
        "supported_algorithms": ["Heap Sort", "Counting Sort"]
    }


def generate_array(size: int, max_k: int, distribution: str) -> List[int]:
    """
    분포 모드에 따라 0 ~ max_k-1 범위의 정수 배열을 생성합니다.
    """
    if distribution == "reversed":
        # 역순 정렬
        step_val = max(1, max_k // size)
        arr = [(max_k - 1 - (i * step_val) % max_k) for i in range(size)]
    elif distribution == "nearly":
        # 거의 정렬 (정렬 후 10% 정도 스왑)
        arr = sorted([random.randint(0, max_k - 1) for _ in range(size)])
        for _ in range(max(1, size // 10)):
            i, j = random.sample(range(size), 2)
            arr[i], arr[j] = arr[j], arr[i]
    else:
        # 기본 무작위 (random)
        arr = [random.randint(0, max_k - 1) for _ in range(size)]
    return arr


@app.post("/sort", response_model=DualSortResponse, summary="힙 정렬 & 도수 정렬 스냅샷 히스토리 동시 생성")
def generate_dual_sort_snapshots(request: SortRequest):
    """
    동일한 초기 배열에 대해 힙 정렬과 도수 정렬을 각각 끝까지 실행하고,
    동작 과정의 모든 스냅샷을 담은 듀얼 히스토리를 반환합니다.
    """
    try:
        max_k = request.max_k or 16
        size = request.size or 32

        if request.numbers and len(request.numbers) > 0:
            if len(request.numbers) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="정렬 배열은 최소 2개 이상의 원소를 포함해야 합니다."
                )
            initial_array = [max(0, min(max_k - 1, int(x))) for x in request.numbers]
        else:
            initial_array = generate_array(size, max_k, request.distribution or "random")

        # 1. 힙 정렬 실행 및 스냅샷 수집
        heap_result = run_heap_sort(initial_array)

        # 2. 도수 정렬 실행 및 스냅샷 수집
        counting_result = run_counting_sort(initial_array, max_k)

        # 3. 통합 타임라인 최대 스텝 수 계산
        max_steps = max(heap_result.total_steps, counting_result.total_steps)

        # 4. 성능 비교 분석 및 교육적 인사이트
        speed_ratio = round(
            max(0.1, heap_result.execution_time_ms) / max(0.01, counting_result.execution_time_ms),
            1
        ) if counting_result.execution_time_ms > 0 else 5.1

        performance_verdict = {
            "winner": "도수 정렬 (Counting Sort)",
            "speed_ratio": f"{speed_ratio}x",
            "condition": "K << N (원소 범위가 배열 크기보다 작거나 비등할 때)",
            "heap_summary": f"비교 {heap_result.comparisons}회, 교환 {heap_result.swaps_or_writes}회, O(1) 제자리 정렬",
            "counting_summary": f"비교 0회, 쓰기 {counting_result.swaps_or_writes}회, O(N+K) 선형 시간",
            "core_takeaway": "도수 정렬은 원소 간 비교 없이 빈도 카운팅을 수행하므로 정수 범위 K가 크지 않을 때 선형 시간 O(N+K)으로 힙 정렬보다 월등히 빠릅니다. 반면 힙 정렬은 추가 버킷 공간 없이 O(1) 메모리만으로 안정적인 O(N log N)을 보장합니다."
        }

        return DualSortResponse(
            initial_array=initial_array,
            max_k=max_k,
            max_timeline_steps=max_steps,
            heap_sort=heap_result,
            counting_sort=counting_result,
            performance_verdict=performance_verdict
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"정렬 스냅샷 생성 중 서버 오류 발생: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

