"""Experimental manual-contract filter; never establishes semantic truth."""

def filter_contract(result, contract):
    if (not isinstance(contract,dict) or set(contract)!={'source_blob','requirements'}
            or contract['source_blob']!=result['source_blob']):
        return {'eligible':[], 'abstained':list(result['accepted']), 'status':'STALE_OR_INVALID_CONTRACT'}
    eligible=[]; abstained=[]
    for claim in result['accepted']:
        conclusion=next(e for e in claim['evidence'] if e['role']=='conclusion')
        key=(conclusion['line'],conclusion['literal'])
        required=contract['requirements'].get(key)
        premises={(e['line'],e['literal']) for e in claim['evidence'] if e['role']=='premise'}
        if required is not None and set(required)<=premises:
            eligible.append(claim)
        else:
            abstained.append(claim)
    return {'eligible':eligible,'abstained':abstained,'status':'MANUAL_REQUIREMENTS_ONLY'}
