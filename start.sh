#!/bin/bash

# arXiv 검색 시스템 시작 스크립트

echo "================================================"
echo "   arXiv 논문 검색 시스템 시작"
echo "================================================"

# 백엔드 설정 확인
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "⚠️  경고: backend/.env 파일이 없습니다."
    echo "env_example.txt를 참고하여 .env 파일을 생성하고"
    echo "GEMINI_API_KEY를 설정해주세요."
    echo ""
    read -p "계속하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 가상 환경 확인
if [ ! -d "backend/venv" ]; then
    echo ""
    echo "📦 Python 가상 환경을 생성합니다..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# 의존성 설치
echo ""
echo "📦 의존성을 설치합니다..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

# 백엔드 서버 시작
echo ""
echo "🚀 백엔드 서버를 시작합니다 (포트 5000)..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# 잠시 대기
sleep 2

# 프론트엔드 서버 시작
echo ""
echo "🌐 프론트엔드 서버를 시작합니다 (포트 8000)..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "================================================"
echo "   ✅ 서버가 성공적으로 시작되었습니다!"
echo "================================================"
echo ""
echo "🌐 브라우저에서 다음 주소로 접속하세요:"
echo "   http://localhost:8000"
echo ""
echo "📡 백엔드 API: http://localhost:5000"
echo ""
echo "중지하려면 Ctrl+C를 누르세요."
echo ""

# 종료 시그널 처리
trap "echo ''; echo '서버를 종료합니다...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGINT SIGTERM

# 대기
wait

