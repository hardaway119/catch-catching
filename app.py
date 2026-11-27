import streamlit as st
import json
from pathlib import Path
from nlp_engine import analyze
from clinical_engine import assess
from question_engine import questions
st.set_page_config(page_title='캐치캐칭 PRO V3.1',page_icon='🚑',layout='wide')
P=json.loads((Path(__file__).parent/'protocols.json').read_text(encoding='utf-8'))
st.title('🚑 캐치캐칭 PRO V3.1')
st.caption('교육·시연용 규칙 기반 시제품 | 실제 출동·처치 결정에 사용하지 않음 | 2023 지침 기반')
for k,v in {'initial':None,'final':None,'case':0,'issued':None}.items():
    if k not in st.session_state: st.session_state[k]=v
def run(t):
    f=analyze(t); c,a=assess(f); return {'text':t,'findings':f,'candidates':c,'alerts':a}
def show(r):
    for a in r['alerts']: st.error(a)
    if r['findings']: st.dataframe(r['findings'],hide_index=True,use_container_width=True)
    for k,v in r['candidates'].items(): st.write('**'+k+'** — '+', '.join(v))
    if not r['candidates']: st.warning('등록 단서 부족: 중증질환 배제 불가. 공식 수보 프로토콜 적용.')
DEMOS={"심혈관 시연":("날이 더워서 그런가 밭에서 일하다가 갑자기 식은땀이 나고 속이 미식거린당께요.","물어보니까 가슴이 꽉 조이고 왼쪽 팔까지 아프다고 하네요."),"뇌혈관 시연":("아부지가 아침부터 어질어질하다더니 술 먹은 사람마냥 비틀거린당께요.","아침 7시까지는 멀쩡했는데 지금은 말도 어눌하고 물건이 두 개로 보인대요.")}
def reset(demo=None):
    for k in list(st.session_state): del st.session_state[k]
    st.session_state.update(initial=None,final=None,issued=None,case=0,call=DEMOS[demo][0] if demo else '',demo=demo)
cols=st.columns(3)
for col,name in zip(cols,DEMOS): col.button(name,on_click=reset,args=(name,))
cols[2].button('초기화',on_click=reset)
t1,t2=st.tabs(['📞 상황실','🚑 구급대'])
with t1:
    st.info('위치·연락처·의식·정상 호흡 우선 확인. 추가 질문 때문에 긴급출동을 지연하지 마세요. (표준지침 p.156)')
    text=st.text_area('STEP 1. 초기 신고 (비식별 가상 사례만)',key='call')
    if st.button('신고 분석',disabled=not text.strip()):
        st.session_state.initial=run(text); st.session_state.final=None; st.session_state.issued=None; st.session_state.case+=1
    r=st.session_state.initial
    if r:
        st.subheader('STEP 2. 단서 및 추가 질문'); show(r)
        for i,q in enumerate(questions(r['candidates']),1): st.write(f'{i}. {q}')
        added=st.text_area('추가 답변 (질문 대상 증상을 포함해 입력)',key=f'added{st.session_state.case}',value=DEMOS.get(st.session_state.get('demo'),('',''))[1])
        if st.button('종합 재분석'):
            st.session_state.final=run(r['text']+'\n'+added); st.session_state.final['added']=added; st.session_state.issued=None
        if st.session_state.final:
            st.subheader('STEP 3. 종합 분석'); show(st.session_state.final); 
            if st.session_state.final['added']==added and r['text']==text and st.button('접보요원 판단 · 시연 출동 명령'):
                from dispatch import issue
                st.session_state.issued=issue(st.session_state.final)
            if st.session_state.issued: st.success('시연 지령 발령 및 태블릿 표출 완료 (동일 세션)')
with t2:
    r=st.session_state.issued
    if not r: st.info('상황실 분석 결과 대기 중')
    else:
        left,right=st.columns(2)
        with left:
            st.subheader('출동지령서 (시연용)')
            st.write('지령번호: '+r['id'])
            st.write('발령: '+r['time'])
            st.write('출동대: 가상 119구급대')
            st.write('장소: 가상 신고 장소 · 지도 미연동')
            st.write(r['text'])
        with right:
            st.subheader('현장 구급태블릿')
            st.write('수신 지령: '+r['id']); show(r)
        opts=list(r['candidates'])+[k for k in P if k not in r['candidates']]
        k=st.selectbox('구급대원 추정질환 / 적용 지침 선택',['선택하지 않음']+opts,key=f'select{st.session_state.case}')
        if k in P:
            p=P[k]
            for field,label in [('assessment','환자평가'),('care','처치 참고'),('caution','주의사항·금기')]:
                st.subheader(label)
                for item in p[field]: st.write('• '+item)
            st.caption(p['source']+' | 최신 개정 및 지역 지침 확인 필요')
            st.subheader('지참 장비 제안 (공식 필수 목록 아님)')
            for i,item in enumerate(p['equipment']): st.checkbox(item,key=f'{st.session_state.case}-{k}-{i}')
