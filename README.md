# 📚 arXiv 논문 검색 시스템

Gemini AI 기반 스마트 논문 검색 시스템입니다. 사용자가 입력한 주제를 Gemini AI가 세분화된 하위 주제 3개로 나누고, 선택한 주제에 대해 arXiv API에서 관련 논문을 검색하여 다운로드할 수 있습니다.

## 🎯 주요 기능

1. **AI 기반 주제 확장**: Gemini AI가 사용자 입력을 전문적인 연구 하위 주제로 세분화
2. **직관적인 주제 선택**: 3개의 카드 형태로 제공되는 하위 주제 중 선택
3. **arXiv 논문 검색**: 선택된 주제로 관련 논문 자동 검색
4. **논문 다운로드**: 개별 PDF 또는 다중 선택 시 ZIP 파일로 다운로드
5. **반응형 UI**: 모던하고 깔끔한 사용자 인터페이스

## 🏗️ 프로젝트 구조

```
arxiv-search-app/
├── backend/
│   ├── app.py              # Flask API 서버
│   ├── requirements.txt    # Python 의존성
│   └── env_example.txt     # 환경 변수 예시
└── frontend/
    ├── index.html          # 메인 HTML
    ├── style.css           # 스타일시트
    └── app.js              # 프론트엔드 로직
```

## 🚀 설치 및 실행

### 1. 필수 요구사항

- Python 3.8 이상
- Gemini API 키 (Google AI Studio에서 발급)

### 2. 백엔드 설정

```bash
cd backend

# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
# .env 파일 생성 후 아래 내용 추가:
# GEMINI_API_KEY=your_actual_api_key_here
```

**Gemini API 키 발급 방법:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Get API Key" 클릭
3. 생성된 API 키를 복사하여 `.env` 파일에 저장

### 3. 백엔드 서버 실행

```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 4. 프론트엔드 실행

새 터미널에서:

```bash
cd frontend

# 간단한 HTTP 서버 실행
python -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 열어 애플리케이션을 사용합니다.

## 📖 사용 방법

1. **주제 입력**: 검색창에 관심 있는 연구 주제를 입력합니다.
   - 예: "Large Language Models", "Quantum Computing", "Climate Change"

2. **하위 주제 선택**: Gemini AI가 제안한 3개의 세부 주제 중 하나를 선택합니다.

3. **논문 검색**: 자동으로 arXiv에서 관련 논문을 검색합니다.

4. **논문 다운로드**: 
   - 원하는 논문을 체크박스로 선택
   - "다운로드" 버튼 클릭
   - 단일 논문은 PDF로, 여러 논문은 ZIP 파일로 다운로드됩니다.

## 🔌 API 엔드포인트

### POST `/api/expand`
사용자 입력을 Gemini AI로 3개의 하위 주제로 확장합니다.

**요청:**
```json
{
  "query": "Large Language Models"
}
```

**응답:**
```json
{
  "subtopics": [
    {
      "title": "Retrieval-Augmented Generation (RAG)",
      "description": "외부 지식 검색 및 결합"
    },
    {
      "title": "Hallucination Mitigation",
      "description": "사실성 향상 및 오류 검증"
    },
    {
      "title": "Domain-Specific Fine-Tuning",
      "description": "도메인별 미세조정"
    }
  ]
}
```

### GET `/api/search`
선택된 주제로 arXiv API에서 논문을 검색합니다.

**파라미터:**
- `query`: 검색 쿼리 (필수)
- `max_results`: 최대 결과 수 (기본값: 10)

**응답:**
```json
{
  "papers": [
    {
      "id": "2301.12345",
      "title": "논문 제목",
      "authors": "저자1, 저자2",
      "summary": "논문 요약",
      "published": "2023-01-15",
      "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf"
    }
  ],
  "total": 10
}
```

### POST `/api/download`
선택된 논문들을 다운로드합니다.

**요청:**
```json
{
  "paper_ids": ["2301.12345", "2302.67890"]
}
```

**응답:** PDF 또는 ZIP 파일 (바이너리)

## 🛠️ 기술 스택

### 백엔드
- **Flask**: 경량 웹 프레임워크
- **Google Generative AI (Gemini)**: 주제 확장 AI
- **Requests**: HTTP 클라이언트
- **arXiv API**: 논문 검색

### 프론트엔드
- **HTML5/CSS3**: 마크업 및 스타일
- **Vanilla JavaScript**: 클라이언트 로직
- **Fetch API**: 비동기 HTTP 요청


## 👥 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📧 문의

문제가 발생하면 GitHub Issues에 등록해주세요.

