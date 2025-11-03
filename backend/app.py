import os
import json
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from io import BytesIO
from zipfile import ZipFile
import urllib.parse

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-pro')
else:
    print("경고: GEMINI_API_KEY가 설정되지 않았습니다.")
    model = None

# arXiv API 기본 URL
ARXIV_API_URL = "http://export.arxiv.org/api/query"


def parse_arxiv_response(xml_content):
    """arXiv API XML 응답을 파싱하여 논문 정보 추출"""
    try:
        root = ET.fromstring(xml_content)
        
        # XML 네임스페이스 정의
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        papers = []
        entries = root.findall('atom:entry', namespaces)
        
        for entry in entries:
            # 기본 정보 추출
            title = entry.find('atom:title', namespaces)
            summary = entry.find('atom:summary', namespaces)
            published = entry.find('atom:published', namespaces)
            
            # 저자 정보 추출
            authors = []
            for author in entry.findall('atom:author', namespaces):
                name = author.find('atom:name', namespaces)
                if name is not None:
                    authors.append(name.text)
            
            # PDF 링크 추출
            pdf_link = None
            for link in entry.findall('atom:link', namespaces):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href')
                    break
            
            # arXiv ID 추출
            arxiv_id = entry.find('atom:id', namespaces)
            if arxiv_id is not None:
                arxiv_id = arxiv_id.text.split('/abs/')[-1]
            
            paper = {
                'id': arxiv_id,
                'title': title.text.strip() if title is not None else 'N/A',
                'authors': ', '.join(authors) if authors else 'N/A',
                'summary': summary.text.strip() if summary is not None else 'N/A',
                'published': published.text[:10] if published is not None else 'N/A',
                'pdf_url': pdf_link
            }
            papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"XML 파싱 오류: {e}")
        return []


@app.route('/api/expand', methods=['POST'])
def expand_topic():
    """사용자 입력을 Gemini를 통해 3개의 하위 주제로 확장"""
    try:
        data = request.get_json()
        user_input = data.get('query', '').strip()
        
        if not user_input:
            return jsonify({'error': '검색어를 입력해주세요.'}), 400
        
        if not model:
            return jsonify({'error': 'Gemini API 키가 설정되지 않았습니다.'}), 500
        
        # Gemini 프롬프트 구성 - JSON 모드
        prompt = f"""당신은 AI 연구 논문 전문가입니다. 사용자가 입력한 내용을 기반으로 arXiv에서 검색하기 위해 키워드를 확장해주세요.

예를 들어, 사용자가 "VLM인데 Vision과 Language가 어떻게 결합되는지 궁금합니다"라고 입력하면, "VLM linear projection"과 같은 구체적인 검색 키워드를 제안해주세요.

입력 주제: "{user_input}"

각 키워드는 arXiv 검색에 최적화된 영어 키워드여야 합니다.
각 설명은 해당 키워드가 무엇을 다루는지 3-4개의 짧은 문장으로 영어로 설명해주세요.
정확히 3개의 키워드를 제안해주세요.

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
    "keywords": {{
        "keyword1": "검색 키워드 1",
        "description1": "키워드 1에 대한 설명",
        "keyword2": "검색 키워드 2",
        "description2": "키워드 2에 대한 설명",
        "keyword3": "검색 키워드 3",
        "description3": "키워드 3에 대한 설명"
    }}
}}
"""
        
        # Gemini API 호출 with JSON mode
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7
            )
        )
        
        response_text = response.text.strip()
        print(f"=== Gemini 응답 ===\n{response_text}\n==================")
        
        # JSON 파싱 - 코드 블록 제거
        json_text = response_text
        
        # 코드 블록 제거
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        print(f"=== 추출된 JSON ===\n{json_text}\n==================")
        
        # JSON 파싱
        parsed_data = json.loads(json_text)
        
        # keywords 객체에서 키워드 추출
        keywords_data = parsed_data.get('keywords', {})
        
        subtopics = [
            {
                'title': keywords_data.get('keyword1', f'{user_input} aspect 1'),
                'description': keywords_data.get('description1', f'Research related to {user_input}')
            },
            {
                'title': keywords_data.get('keyword2', f'{user_input} aspect 2'),
                'description': keywords_data.get('description2', f'Research related to {user_input}')
            },
            {
                'title': keywords_data.get('keyword3', f'{user_input} aspect 3'),
                'description': keywords_data.get('description3', f'Research related to {user_input}')
            }
        ]
        
        print(f"=== 최종 subtopics ===\n{json.dumps(subtopics, indent=2, ensure_ascii=False)}\n====================")
        
        return jsonify({'subtopics': subtopics})
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500


@app.route('/api/search', methods=['GET'])
def search_arxiv():
    """선택된 주제로 arXiv API 검색"""
    try:
        query = request.args.get('query', '').strip()
        max_results = request.args.get('max_results', '10')
        
        if not query:
            return jsonify({'error': '검색어를 입력해주세요.'}), 400
        
        # arXiv API 쿼리 구성
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': int(max_results),
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        # arXiv API 호출
        response = requests.get(ARXIV_API_URL, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'arXiv API 호출 실패'}), 500
        
        # XML 응답 파싱
        papers = parse_arxiv_response(response.content)
        
        return jsonify({
            'papers': papers,
            'total': len(papers)
        })
    
    except Exception as e:
        print(f"검색 오류: {e}")
        return jsonify({'error': f'검색 중 오류 발생: {str(e)}'}), 500


@app.route('/api/download', methods=['POST'])
def download_papers():
    """선택된 논문들을 다운로드 (단일 PDF 또는 ZIP)"""
    try:
        data = request.get_json()
        paper_ids = data.get('paper_ids', [])
        
        if not paper_ids:
            return jsonify({'error': '다운로드할 논문을 선택해주세요.'}), 400
        
        # 단일 논문인 경우
        if len(paper_ids) == 1:
            pdf_url = f"https://arxiv.org/pdf/{paper_ids[0]}.pdf"
            response = requests.get(pdf_url)
            
            if response.status_code == 200:
                return send_file(
                    BytesIO(response.content),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f"{paper_ids[0]}.pdf"
                )
            else:
                return jsonify({'error': 'PDF 다운로드 실패'}), 500
        
        # 여러 논문인 경우 ZIP으로 묶기
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for paper_id in paper_ids:
                pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
                response = requests.get(pdf_url)
                
                if response.status_code == 200:
                    zip_file.writestr(f"{paper_id}.pdf", response.content)
        
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='arxiv_papers.zip'
        )
    
    except Exception as e:
        print(f"다운로드 오류: {e}")
        return jsonify({'error': f'다운로드 중 오류 발생: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'gemini_configured': GEMINI_API_KEY is not None
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

