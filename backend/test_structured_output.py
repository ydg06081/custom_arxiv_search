#!/usr/bin/env python3
"""
Structured Output 기능 테스트 스크립트
"""
import os
import json
import google.generativeai as genai

# API 키 확인
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
    print("\n다음 명령어로 API 키를 설정하세요:")
    print('export GEMINI_API_KEY="your-api-key-here"')
    exit(1)

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

# 테스트 쿼리
user_input = "VLM인데 Vision과 Language가 어떻게 결합되는지 궁금합니다"

print(f"🔍 테스트 쿼리: {user_input}\n")
print("=" * 80)

# 프롬프트
prompt = f"""당신은 AI 연구 논문 전문가입니다. 사용자가 입력한 내용을 기반으로 arXiv에서 검색하기 위해 키워드를 확장해주세요.

예를 들어, 사용자가 "VLM인데 Vision과 Language가 어떻게 결합되는지 궁금합니다"라고 입력하면, "VLM linear projection"과 같은 구체적인 검색 키워드를 제안해주세요.

입력 주제: "{user_input}"

각 키워드는 arXiv 검색에 최적화된 영어 키워드여야 합니다.
각 설명은 해당 키워드가 무엇을 다루는지 3-4개의 짧은 문장으로 영어로 설명해주세요.
정확히 3개의 키워드를 제안해주세요.
"""

# Structured Output 스키마
response_schema = {
    "type": "object",
    "properties": {
        "keywords": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "arXiv 검색에 최적화된 영어 키워드"
                    },
                    "description": {
                        "type": "string",
                        "description": "키워드에 대한 3-4문장의 영어 설명"
                    }
                },
                "required": ["keyword", "description"]
            },
            "minItems": 3,
            "maxItems": 3
        }
    },
    "required": ["keywords"]
}

print("📡 Gemini API 호출 중...\n")

try:
    # API 호출
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json",
            response_schema=response_schema
        )
    )
    
    print("✅ API 호출 성공!\n")
    print("=" * 80)
    print("📋 Gemini 구조화된 응답:")
    print("=" * 80)
    
    # JSON 파싱
    parsed_data = json.loads(response.text)
    print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("🎯 최종 subtopics 변환:")
    print("=" * 80)
    
    # subtopics 변환
    keywords_list = parsed_data.get('keywords', [])
    subtopics = [
        {
            'title': kw.get('keyword', f'{user_input} aspect {i+1}'),
            'description': kw.get('description', f'Research related to {user_input}')
        }
        for i, kw in enumerate(keywords_list[:3])
    ]
    
    # 3개 미만일 경우 기본값으로 채우기
    while len(subtopics) < 3:
        idx = len(subtopics) + 1
        subtopics.append({
            'title': f'{user_input} aspect {idx}',
            'description': f'Research related to {user_input}'
        })
    
    print(json.dumps({'subtopics': subtopics}, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료!")
    print("=" * 80)
    print("\n💡 Structured Output의 장점:")
    print("  - ✅ 항상 정확한 JSON 형식 반환")
    print("  - ✅ 코드 블록 제거 로직 불필요")
    print("  - ✅ 파싱 오류 가능성 최소화")
    print("  - ✅ 스키마 검증 자동화")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

