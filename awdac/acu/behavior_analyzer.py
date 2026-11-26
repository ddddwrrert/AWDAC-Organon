from collections import Counter

def summarize(traces):
    return dict(Counter(trace["event"] for trace in traces))
