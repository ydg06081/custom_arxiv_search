# 🚀 빠른 시작 가이드

## 📋 설치 전 체크리스트

- [ ] Python 3.8 이상 설치 확인
- [ ] Gemini API 키 발급 ([Google AI Studio](https://makersuite.google.com/app/apikey))

## ⚡ 빠른 시작 (자동)

### Linux/Mac

```bash
cd arxiv-search-app
./start.sh
```

### Windows

```cmd
cd arxiv-search-app
start.bat
```

스크립트가 자동으로 다음을 수행합니다:
1. Python 가상 환경 생성
2. 의존성 패키지 설치
3. 백엔드 서버 시작 (포트 5000)
4. 프론트엔드 서버 시작 (포트 8000)

## 🔧 수동 설정

### 1단계: 환경 변수 설정

```bash
cd backend
cp .env_template .env
```

`.env` 파일을 열고 Gemini API 키를 입력하세요:

```
GEMINI_API_KEY=실제_발급받은_API_키_입력
```

### 2단계: 백엔드 설정

```bash
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 3단계: 백엔드 서버 실행

```bash
python app.py
```

✅ 서버가 `http://localhost:5000`에서 실행됩니다.

### 4단계: 프론트엔드 서버 실행 (새 터미널)

```bash
cd frontend
python -m http.server 8000
```

✅ 프론트엔드가 `http://localhost:8000`에서 실행됩니다.

### 5단계: 브라우저에서 접속

브라우저에서 `http://localhost:8000`을 열어주세요.

## 🧪 테스트

1. **검색창에 주제 입력**: "Large Language Models"
2. **하위 주제 확인**: Gemini가 제안한 3개의 세부 주제 확인
3. **주제 선택**: 관심 있는 주제 클릭
4. **논문 검색 결과**: arXiv에서 검색된 논문 목록 확인
5. **논문 다운로드**: 체크박스로 선택 후 다운로드

## ❓ 문제 해결

### Gemini API 오류

**증상**: "Gemini API 키가 설정되지 않았습니다" 오류

**해결**:
1. `backend/.env` 파일 존재 확인
2. API 키가 올바르게 입력되었는지 확인
3. 백엔드 서버 재시작

### CORS 오류

**증상**: 브라우저 콘솔에 CORS 관련 오류

**해결**:
1. 백엔드 서버가 5000번 포트에서 실행 중인지 확인
2. 프론트엔드가 8000번 포트에서 실행 중인지 확인
3. 방화벽 설정 확인

### 포트 충돌

**증상**: "Address already in use" 오류

**해결**:

```bash
# 다른 포트 사용 (예: 5001, 8001)
# 백엔드
python app.py --port 5001

# 프론트엔드
python -m http.server 8001
```

그리고 `frontend/app.js`의 `API_BASE_URL`을 수정하세요.

## 🎯 다음 단계

- 논문 검색 시 다양한 주제로 테스트
- 검색 결과 개수 조정 (`max_results` 파라미터)
- UI 커스터마이징 (`frontend/style.css`)

## 📚 추가 자료

- [Gemini API 문서](https://ai.google.dev/docs)
- [arXiv API 문서](https://arxiv.org/help/api)
- [Flask 문서](https://flask.palletsprojects.com/)

## 💡 팁

1. **API 키 보안**: `.env` 파일을 Git에 커밋하지 마세요 (`.gitignore`에 이미 포함됨)
2. **성능**: 검색 결과가 많을 경우 `max_results` 값을 조정하세요
3. **커스터마이징**: CSS 변수를 수정하여 색상 테마를 변경할 수 있습니다

