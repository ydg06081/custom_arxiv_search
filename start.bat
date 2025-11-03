@echo off
REM arXiv 검색 시스템 시작 스크립트 (Windows)

echo ================================================
echo    arXiv 논문 검색 시스템 시작
echo ================================================

REM 백엔드 설정 확인
if not exist "backend\.env" (
    echo.
    echo [경고] backend\.env 파일이 없습니다.
    echo env_example.txt를 참고하여 .env 파일을 생성하고
    echo GEMINI_API_KEY를 설정해주세요.
    echo.
    pause
)

REM 가상 환경 확인
if not exist "backend\venv" (
    echo.
    echo [정보] Python 가상 환경을 생성합니다...
    cd backend
    python -m venv venv
    cd ..
)

REM 의존성 설치
echo.
echo [정보] 의존성을 설치합니다...
cd backend
call venv\Scripts\activate
pip install -q -r requirements.txt
cd ..

REM 백엔드 서버 시작
echo.
echo [정보] 백엔드 서버를 시작합니다 (포트 5000)...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python app.py"

REM 잠시 대기
timeout /t 3 /nobreak > nul

REM 프론트엔드 서버 시작
echo.
echo [정보] 프론트엔드 서버를 시작합니다 (포트 8000)...
start "Frontend Server" cmd /k "cd frontend && python -m http.server 8000"

echo.
echo ================================================
echo    서버가 성공적으로 시작되었습니다!
echo ================================================
echo.
echo [정보] 브라우저에서 다음 주소로 접속하세요:
echo        http://localhost:8000
echo.
echo [정보] 백엔드 API: http://localhost:5000
echo.
echo [정보] 서버를 종료하려면 각 창을 닫으세요.
echo.
pause

