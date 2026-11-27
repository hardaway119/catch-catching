import re,json
from pathlib import Path
from collections import defaultdict
BASE=Path(__file__).parent
EXTRA={'흉통':['가슴은안아파','가슴이안아파','가슴은아프','가슴이아팠','가슴은안아프','가슴이아프지','가슴이아픈지'],'흉부압박감':['가슴이꽉막','가슴이조여','가슴이답답','가슴은답답'],'호흡곤란':['숨이안쉬어','숨이차지','숨은차지'],'편측 근력저하':['한쪽팔에힘이없','한쪽다리에힘이없','편마비','한쪽팔다리마비','한쪽팔이안올라'],'언어 이상':['말이어눌','발음이어눌','말을못','말이안나','말이꼬'],'안면 이상':['입이돌아','안면마비','얼굴한쪽이처','입꼬리가처'],'두통':['두통','머리가깨','머리가아프'],'고온 노출':['폭염','더운곳','더운환경','더워','여름','햇볕','열사병','고온'],'저혈당 단서':['저혈당','인슐린','공복','밥을못먹','손떨'],'비정상 호흡':['숨을안쉬','호흡없','숨을쉬지않','헐떡','숨이없']}
SKIP={'부정·불확실 단서','활동·자세 단서'}
def norm(s): return re.sub(r'\s+','',s.lower())
def analyze(text):
    groups=defaultdict(set)
    for r in json.loads((BASE/'cardio_keywords.json').read_text(encoding='utf-8')):
        if r['category'] not in SKIP: groups[r['category']].add(r['pattern'])
    for k,v in EXTRA.items(): groups[k].update(v)
    mapping={'face':'안면 이상','arm':'편측 근력저하','leg':'편측 근력저하','dysarthria':'언어 이상','aphasia':'언어 이상','balance':'보행장애','coordination':'보행장애','diplopia':'복시','vision':'시각 이상','sensory':'편측 감각 이상','gaze':'안구편위','dysphagia':'연하장애','headache':'두통','vertigo':'어지럼','consciousness':'의식 이상','seizure':'경련','vomit':'구토','onset':'급성 발현','resolved':'증상 소실','wake':'기상 시 발견','chest':'흉부압박감','dyspnea':'호흡곤란','sweat':'발한','nausea':'오심','collapse':'실신·쓰러짐','breathing':'비정상 호흡'}
    for r in json.loads((BASE/'expressions.json').read_text(encoding='utf-8')):
        if r['concept_id'] in mapping: groups[mapping[r['concept_id']]].add(norm(r['expression']))
    additions={'고온 노출':['날이더워','밭에서일','더운날'],'오심':['미식거','메슥','울렁'],'흉부압박감':['가슴이꽉조','가슴이조이','가슴이쪼이'],'방사 가능 위치':['왼쪽팔까지아프','왼팔까지아프'],'어지럼':['어질어질','어지러','어질허'],'보행장애':['비틀거','중심을못잡','한쪽으로쏠','다리를질질'],'복시':['두개로보','겹쳐보'],'언어 이상':['말도어눌','발음이뭉개','혀가꼬','말이이상'],'급성 발현':['갑자기','방금'],'증상 소실':['지금은괜찮','마비가풀','증상이사라'],'최종 정상 시간 단서':['까지는멀쩡','까지정상','마지막으로정상'],'편측 근력저하':['한쪽팔을못들','오른팔을못들','왼팔을못들'],'두통':['머리를망치로맞','머리가터질'],'발한':['식은땀','진땀']}
    for k,v in additions.items(): groups[k].update(v)
    out=[]
    for clause in re.split(r'[,.!?;\n]|는데|지만|않고|(?<=없고)|(?<=있고)|(?<=나고)|(?<=하고)',text):
        s=norm(clause)
        for cat,patterns in groups.items():
            matches=[]
            for p in sorted(patterns,key=lambda x:(-len(x),x)):
                for m in re.finditer(re.escape(p),s):
                    if any(m.start()<b and m.end()>a for a,b in matches): continue
                    matches.append(m.span()); a,b=m.span(); before=s[max(0,a-8):a]; after=s[b:b+9]; token=m.group()
                    status='현재'
                    if cat=='심혈관 병력 단서': status='병력/언급 확인 필요'
                    if re.search(r'가족력',before+after): status='주체 확인 필요'
                    if re.search(r'과거|예전|작년|병력|이력|앓았|진단받',before+after): status='과거력'
                    if re.search(r'어제|지난|아팠',before+token+after): status='시점 확인 필요'
                    if re.search(r'모르|것같|인지|의심',after): status='불확실'
                    if re.search(r'^(?:은|는|이|가|도|증상|통증|이전혀)*\s*(?:없|아니|않|안아프|안아파|지않)',after) or (cat=='흉통' and re.search(r'안아[프파]',token)) or (cat=='호흡곤란' and re.search(r'차지않',token+after)):
                        if cat not in {'의식 이상','편측 근력저하','비정상 호흡'}: status='부정'
                    if re.search(r'없는건아니|없지는않|마비는없|어눌하지않|비틀거리지않|두개로보이지않',s) and cat in {'편측 근력저하','언어 이상','보행장애','복시'}: status='부정'
                    out.append({'category':cat,'expression':token,'status':status})
    return list({(x['category'],x['expression'],x['status']):x for x in out}.values())
