from copy import deepcopy
from datetime import datetime, timezone, timedelta
from uuid import uuid4

def issue(result):
    if not result or 'added' not in result:
        raise ValueError('종합 분석 후 접보요원이 발령해야 합니다.')
    return dict(deepcopy(result), id='DEMO-'+uuid4().hex[:8], time=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds'))
