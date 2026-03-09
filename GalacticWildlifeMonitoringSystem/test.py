a = [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 91},
    {"name": "Eve", "score": 78}
]
b = sorted(a, key=lambda x: x["score"] or '', reverse=True)[:10]
print(b)