from nottingham_grader import calculate_metrics

def test_nottingham_grader_single():
    result=calculate_metrics(v1=1,v2=2,v3=3)
    assert result["score"]==6
    assert result["grade"]==2
