import streamlit as st
import time

# --- 1. 상태 저장 ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'disease_type' not in st.session_state:
    st.session_state.disease_type = ""
if 'call_text' not in st.session_state:
    st.session_state.call_text = ""
if 'added_info' not in st.session_state:
    st.session_state.added_info = ""
if 'detected_keywords' not in st.session_state:
    st.session_state.detected_keywords = ""
if 'next_questions' not in st.session_state:
    st.session_state.next_questions = ""

# --- 2. 🚨 엑셀 기반 딥러닝 모사 키워드 사전 ---
# 주변 증상(약한 단서)과 핵심 증상(강력 단서)을 분리
cerebro_core = ["마비", "편마비", "힘빠", "힘이없", "거동불가", "어눌", "발음", "말을못", "안면마비", "입돌아", "침흘", "눈이풀", "의식저하", "쓰러"]
cerebro_sub = ["어지럽", "어질", "핑돈", "두통", "머리깨", "기력"]

cardio_core = ["가슴", "흉통", "명치", "심장", "어깨", "턱", "왼팔", "방사통", "쥐어짜", "짓누르", "숨쉬기", "숨차", "식은땀", "진땀"]
cardio_sub = ["소화", "체한", "얹힌", "메스껍", "울렁", "구토", "토할", "답답"]

heat_keywords = ["더워", "폭염", "땀이많이", "열사병"]

def extract_keywords(text, keyword_list):
    text = text.replace(" ", "")
    return [kw for kw in keyword_list if kw in text]

# --- 3. 앱 화면 구성 ---
st.set_page_config(page_title="캐치캐칭 - 119 구급현장 길라잡이", page_icon="🚑", layout="centered")
st.markdown("<h1 style='text-align: center; color: #ff4757;'>🚑 캐치캐칭 PRO</h1>", unsafe_allow_html=True)
st.write("---")

tab1, tab2 = st.tabs(["📞 상황실 (AI 문맥 분석)", "🚑 구급대 (출동지령서)"])

# ==========================================
# 탭 1: 상황실 (Dispatcher View)
# ==========================================
with tab1:
    st.subheader("[STEP 1] 119 초기 신고 내용 접수")
    call_input = st.text_area("신고 내용을 입력하세요.", placeholder="예: 밥 먹는데 체했는지 명치가 답답해요.", height=100)
    
    if st.button("AI 신고 분석 및 상황실 역질문 도출", use_container_width=True):
        if call_input:
            with st.spinner('신고 데이터 기반 문맥 및 증상 연관성 분석 중... ⏳'):
                time.sleep(1.0) # AI가 생각하는 듯한 시각적 효과 연출
                st.session_state.step = 0
                st.session_state.call_text = call_input
                
                # 키워드 스캔
                ce_core = extract_keywords(call_input, cerebro_core)
                ce_sub = extract_keywords(call_input, cerebro_sub)
                ca_core = extract_keywords(call_input, cardio_core)
                ca_sub = extract_keywords(call_input, cardio_sub)
                ht_key = extract_keywords(call_input, heat_keywords)

                if ht_key and not ca_core and not ca_sub:
                    st.info("✅ **[AI 분석] 온열질환 또는 단순 발한 감지**")
                    st.warning("💡 **[AI 역질문]** 심근경색 감별을 위해 \"가슴이 답답하거나 아프진 않나요?\" 질문 요망")
                
                elif ce_core or ce_sub:
                    st.session_state.disease_type = "뇌졸중"
                    st.session_state.step = 1
                    found_words = ce_core + ce_sub
                    st.session_state.detected_keywords = " ".join([f"<span style='background-color:#ffeaa7; padding:4px 8px; border-radius:4px; font-weight:bold; color:black;'>#{w}</span>" for w in set(found_words)])
                    
                    if ce_core: # 핵심 증상이 바로 들어온 경우
                        st.session_state.next_questions = "1️⃣ **최종 정상 시간(LKW) 확인:** \"마지막으로 환자분이 멀쩡했던 시간이 언제인가요?\"\n2️⃣ **추가 마비 확인:** \"팔다리를 들어보라고 하실 때 한쪽만 떨어지나요?\""
                    else: # 두통/어지럼증 등 주변 증상만 들어온 경우
                        st.session_state.next_questions = "1️⃣ **안면 마비 확인:** \"미소를 지어보라 하실 때 얼굴 한쪽이 처지거나 침을 흘리나요?\"\n2️⃣ **언어 장애 확인:** \"발음이 어눌해지거나 엉뚱한 대답을 하시나요?\""

                elif ca_core or ca_sub:
                    st.session_state.disease_type = "심근경색"
                    st.session_state.step = 1
                    found_words = ca_core + ca_sub
                    st.session_state.detected_keywords = " ".join([f"<span style='background-color:#81ecec; padding:4px 8px; border-radius:4px; font-weight:bold; color:black;'>#{w}</span>" for w in set(found_words)])
                    
                    if ca_core: # 가슴 통증 등 핵심 증상
                        st.session_state.next_questions = "1️⃣ **방사통 여부 확인:** \"통증이 가슴에서 어깨, 턱, 왼쪽 팔로 퍼지나요?\"\n2️⃣ **의식 상태 확인:** \"환자분이 의식이 흐려지거나 쓰러지려 하나요?\""
                    else: # 소화불량, 구토 등 주변 증상
                        st.session_state.next_questions = "1️⃣ **흉통 동반 확인:** \"소화가 안되면서 가슴이 쥐어짜듯 아프거나 짓누르진 않나요?\"\n2️⃣ **발한 여부 확인:** \"갑자기 식은땀을 비 오듯 심하게 흘리시나요?\""
                else:
                    st.success("✅ **[AI 분석] 일반 구급 출동** (중증 특이 키워드 미감지)")

    # 1차 분석 결과 및 추가 질문 폼
    if st.session_state.step >= 1:
        st.write("---")
        st.subheader("[STEP 2] 초기 단서 감지 및 맞춤형 역질문")
        
        st.error(f"🚨 **[AI 단서 포착] {st.session_state.disease_type} 관련 증상 감지**")
        st.markdown(f"💡 **신고 내용 내 핵심 단어:** {st.session_state.detected_keywords}", unsafe_allow_html=True)
        
        st.warning(f"💡 **[AI 상황실 역질문 프롬프트]** 중증 감별을 위해 신고자에게 아래 사항을 즉시 질문하세요.\n\n{st.session_state.next_questions}")
        
        added_q = st.text_area("📞 신고자 역질문 확인 결과 입력", placeholder="예: 가슴이 쥐어짜듯 아프고 식은땀이 난다고 함", height=70)
        
        if st.button("질환 확정 및 구급대 출동 지령", type="primary", use_container_width=True):
            with st.spinner('최종 종합 소견 및 지령서 작성 중... ⏳'):
                time.sleep(1.0)
                st.session_state.added_info = added_q
                st.session_state.step = 2

    # 2차 확정 결과 및 지령 알림
    if st.session_state.step == 2:
        st.write("---")
        st.subheader("[STEP 3] 최종 예측 확정")
        st.error(f"🚨 **[최종 확정] 급성 {st.session_state.disease_type} 강력 의심. 구급대 출동 요망.**")
        st.success("✅ 관할 구급대에 지령서 및 현장 응급처치 표준지침이 전송되었습니다. '구급대' 탭을 클릭하세요.")

# ==========================================
# 탭 2: 구급대 단말기 (Paramedic View)
# ==========================================
with tab2:
    if st.session_state.step < 2:
        st.info("현재 대기 중입니다. 상황실의 출동 지령을 기다려주세요.")
    else:
        st.markdown("<h2 style='color: #00a8ff;'>🚨 출동 지령서</h2>", unsafe_allow_html=True)
        st.markdown(f"**🔴 추정 질환:** <span style='color: red; font-size: 1.2em; font-weight: bold;'>{st.session_state.disease_type} 확진 대비</span>", unsafe_allow_html=True)
        st.info(f"**[상황실 접수 내용 (초기+추가 종합)]**\n- 초기: {st.session_state.call_text}\n- 역질문 결과: {st.session_state.added_info}")
        
        st.write("---")
        st.subheader("📋 현장응급처치 표준지침 및 주의사항")
        
        if st.session_state.disease_type == "뇌졸중":
            col1, col2 = st.columns(2)
            with col1:
                st.success("**[현장 확인 및 처치]**\n- **CPSS (신시네티 뇌졸중 척도)** 신속 평가\n- **혈당 측정** (저혈당 감별 필수)\n- **LKW (최종 정상 시간)** 정확히 파악")
            with col2:
                st.error("**[⚠️ 처치 주의사항]**\n- 뇌관류압 유지를 위해 **함부로 혈압 강하 금지**\n- 구토 시 흡인성 폐렴 예방 위해 **고개 측면 유지**")
            
        elif st.session_state.disease_type == "심근경색":
            col1, col2 = st.columns(2)
            with col1:
                st.success("**[현장 확인 및 처치]**\n- **12유도 심전도(ECG)** 획득 및 ST분절 상승 확인\n- 산소포화도 94% 미만 시 **산소 투여**\n- 의료지도 후 **아스피린/NTG 투여**")
            with col2:
                st.error("**[⚠️ NTG 투여 절대 금기증 확인]**\n1. 수축기 혈압 **90mmHg 이하**\n2. 우심실 경색 의심 환자\n3. 48시간 내 **발기부전 치료제** 복용")

        st.write("---")
        if st.button("✅ 표준지침 숙지 완료. 지참 장비 목록 확인", use_container_width=True):
            st.subheader("🎒 현장 필수 지참 장비 리스트")
            if st.session_state.disease_type == "뇌졸중":
                st.checkbox("혈당 측정기 세트 (저혈당 감별용)")
                st.checkbox("펜라이트 (동공 반사 및 CPSS 평가용)")
                st.checkbox("구토 대비 휴대용 흡인기 (석션기)")
                st.checkbox("이송용 구급 들것")
            elif st.session_state.disease_type == "심근경색":
                st.checkbox("12유도 심전도(ECG) 모니터 및 부착 패치")
                st.checkbox("구급 약물 배낭 (NTG, 아스피린, N/S 수액)")
                st.checkbox("자동심장충격기(AED)")
                st.checkbox("휴대용 산소 투여 장비")