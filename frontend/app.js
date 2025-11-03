// API 베이스 URL (로컬 개발 환경)
const API_BASE_URL = 'http://localhost:5000';

// 전역 상태
let currentSubtopics = [];
let currentPapers = [];
let selectedPaperIds = new Set();

// DOM 요소
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const subtopicsSection = document.getElementById('subtopics-section');
const subtopicsContainer = document.getElementById('subtopics-container');
const resultsSection = document.getElementById('results-section');
const papersContainer = document.getElementById('papers-container');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const currentTopicDiv = document.getElementById('current-topic');
const currentTopicText = document.getElementById('current-topic-text');
const selectAllBtn = document.getElementById('select-all-btn');
const downloadBtn = document.getElementById('download-btn');
const backBtn = document.getElementById('back-btn');
const selectedCountSpan = document.getElementById('selected-count');

// 이벤트 리스너 설정
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearch();
});
selectAllBtn.addEventListener('click', toggleSelectAll);
downloadBtn.addEventListener('click', handleDownload);
backBtn.addEventListener('click', resetSearch);

// 검색 실행
async function handleSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        showError('검색어를 입력해주세요.');
        return;
    }
    
    hideError();
    showLoading();
    hideSection(subtopicsSection);
    hideSection(resultsSection);
    hideSection(currentTopicDiv);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/expand`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        if (!response.ok) {
            throw new Error('Gemini API 호출 실패');
        }
        
        const data = await response.json();
        currentSubtopics = data.subtopics;
        
        displaySubtopics(data.subtopics);
        showSection(subtopicsSection);
        
    } catch (error) {
        console.error('검색 오류:', error);
        showError('검색 중 오류가 발생했습니다. Gemini API 키를 확인해주세요.');
    } finally {
        hideLoading();
    }
}

// 하위 주제 표시
function displaySubtopics(subtopics) {
    subtopicsContainer.innerHTML = '';
    
    subtopics.forEach((subtopic, index) => {
        const card = document.createElement('div');
        card.className = 'subtopic-card';
        card.innerHTML = `
            <h3>${subtopic.title}</h3>
            <p>${subtopic.description}</p>
            <button class="search-btn" data-index="${index}">이 주제로 검색</button>
        `;
        
        const searchButton = card.querySelector('.search-btn');
        searchButton.addEventListener('click', () => searchWithSubtopic(subtopic));
        
        subtopicsContainer.appendChild(card);
    });
}

// 선택된 하위 주제로 논문 검색
async function searchWithSubtopic(subtopic) {
    hideError();
    showLoading();
    hideSection(subtopicsSection);
    
    // 현재 검색 주제 표시
    currentTopicText.textContent = subtopic.title;
    showSection(currentTopicDiv);
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/search?query=${encodeURIComponent(subtopic.title)}&max_results=20`
        );
        
        if (!response.ok) {
            throw new Error('arXiv API 호출 실패');
        }
        
        const data = await response.json();
        currentPapers = data.papers;
        selectedPaperIds.clear();
        
        displayPapers(data.papers);
        showSection(resultsSection);
        updateDownloadButton();
        
    } catch (error) {
        console.error('논문 검색 오류:', error);
        showError('논문 검색 중 오류가 발생했습니다.');
        showSection(subtopicsSection);
    } finally {
        hideLoading();
    }
}

// 논문 목록 표시
function displayPapers(papers) {
    papersContainer.innerHTML = '';
    
    if (papers.length === 0) {
        papersContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">검색 결과가 없습니다.</p>';
        return;
    }
    
    papers.forEach((paper, index) => {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'paper-item';
        paperDiv.dataset.paperId = paper.id;
        
        paperDiv.innerHTML = `
            <div class="paper-header">
                <input type="checkbox" class="paper-checkbox" data-paper-id="${paper.id}">
                <div class="paper-content">
                    <h3 class="paper-title">${escapeHtml(paper.title)}</h3>
                    <p class="paper-authors">저자: ${escapeHtml(paper.authors)}</p>
                    <p class="paper-date">발행일: ${paper.published}</p>
                    <p class="paper-summary">${escapeHtml(truncateText(paper.summary, 300))}</p>
                    ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank" class="paper-link">PDF 보기 →</a>` : ''}
                </div>
            </div>
        `;
        
        const checkbox = paperDiv.querySelector('.paper-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                selectedPaperIds.add(paper.id);
                paperDiv.classList.add('selected');
            } else {
                selectedPaperIds.delete(paper.id);
                paperDiv.classList.remove('selected');
            }
            updateDownloadButton();
        });
        
        papersContainer.appendChild(paperDiv);
    });
}

// 전체 선택/해제 토글
function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.paper-checkbox');
    const allChecked = selectedPaperIds.size === currentPapers.length;
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
        const paperId = checkbox.dataset.paperId;
        const paperDiv = checkbox.closest('.paper-item');
        
        if (!allChecked) {
            selectedPaperIds.add(paperId);
            paperDiv.classList.add('selected');
        } else {
            selectedPaperIds.delete(paperId);
            paperDiv.classList.remove('selected');
        }
    });
    
    updateDownloadButton();
}

// 다운로드 버튼 상태 업데이트
function updateDownloadButton() {
    const count = selectedPaperIds.size;
    selectedCountSpan.textContent = count;
    downloadBtn.disabled = count === 0;
    selectAllBtn.textContent = count === currentPapers.length ? '전체 해제' : '전체 선택';
}

// 선택된 논문 다운로드
async function handleDownload() {
    if (selectedPaperIds.size === 0) {
        showError('다운로드할 논문을 선택해주세요.');
        return;
    }
    
    hideError();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paper_ids: Array.from(selectedPaperIds)
            })
        });
        
        if (!response.ok) {
            throw new Error('다운로드 실패');
        }
        
        // Blob으로 파일 다운로드
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // 파일명 결정
        if (selectedPaperIds.size === 1) {
            a.download = `${Array.from(selectedPaperIds)[0]}.pdf`;
        } else {
            a.download = 'arxiv_papers.zip';
        }
        
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showError('다운로드가 완료되었습니다!', 'success');
        setTimeout(hideError, 3000);
        
    } catch (error) {
        console.error('다운로드 오류:', error);
        showError('다운로드 중 오류가 발생했습니다.');
    }
}

// 검색 초기화
function resetSearch() {
    hideSection(resultsSection);
    hideSection(currentTopicDiv);
    showSection(subtopicsSection);
    selectedPaperIds.clear();
}

// UI 헬퍼 함수
function showSection(element) {
    element.style.display = 'block';
}

function hideSection(element) {
    element.style.display = 'none';
}

function showLoading() {
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function showError(message, type = 'error') {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    if (type === 'success') {
        errorMessage.style.backgroundColor = '#D1FAE5';
        errorMessage.style.color = '#065F46';
        errorMessage.style.borderLeftColor = '#10B981';
    } else {
        errorMessage.style.backgroundColor = '#FEE2E2';
        errorMessage.style.color = '#DC2626';
        errorMessage.style.borderLeftColor = '#EF4444';
    }
    
    // 화면 상단으로 스크롤
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideError() {
    errorMessage.style.display = 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 초기화
console.log('arXiv 검색 시스템이 준비되었습니다.');

