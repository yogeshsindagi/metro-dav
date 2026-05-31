def compute_fare(hops, rules=None):
    if hops <= 2: return 10
    elif hops <= 4: return 20
    elif hops <= 6: return 30
    elif hops <= 8: return 40
    elif hops <= 10: return 50
    elif hops <= 15: return 60
    elif hops <= 20: return 70
    elif hops <= 25: return 80
    else: return 90