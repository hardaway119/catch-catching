RULES={
'흉통 / 급성관상동맥증후군 감별':{'흉통','흉부압박감','상복부 불편','발한','오심','호흡곤란','심계항진'},
'급성 뇌졸중의증':{'편측 근력저하','언어 이상','안면 이상','두통','어지럼','보행장애','복시','시각 이상','편측 감각 이상','안구편위','연하장애'},
'고온 환경 질환':{'고온 노출'},
'급성 저혈당 의증':{'저혈당 단서','발한','의식 이상'},
}
def assess(findings):
    active={x['category'] for x in findings if x['status'] in ('현재','불확실','시점 확인 필요')}
    candidates={k:sorted(v&active) for k,v in RULES.items() if v&active}
    if '급성 뇌졸중의증' in candidates and not active & {'편측 근력저하','언어 이상','안면 이상','보행장애','복시','시각 이상','편측 감각 이상','안구편위'}: candidates['급성 뇌졸중의증']+=['비특이 단서: 추가 확인 필요']
    alerts=[]
    if active & {'의식 이상','비정상 호흡','실신·쓰러짐'}: alerts.append('의식 및 정상 호흡 즉시 확인. 심정지 의심 시 공식 긴급출동·심폐소생술 프로토콜 우선.')
    if active & {'흉통','흉부압박감'} and active & {'편측 근력저하','언어 이상','안면 이상'}: alerts.append('흉통과 신경학적 이상 동반: 대동맥박리 등 중증 원인도 감별 필요.')
    if active & {'흉통','흉부압박감','호흡곤란'}: alerts.append('폐색전증, 대동맥박리, 기흉 등도 배제되지 않음.')
    if active & {'보행장애','복시','연하장애'}: alerts.append('후방순환 뇌졸중 감별 필요: FAST 정상만으로 배제 불가.')
    if '증상 소실' in active and '급성 뇌졸중의증' in candidates: alerts.append('일시적 신경학적 증상: TIA 등 감별, 호전되어도 응급평가 필요.')
    if '두통' in active and active & {'급성 발현','구토'}: alerts.append('돌발성 심한 두통 여부 확인: 지주막하출혈 등 감별.')
    return candidates,alerts
