import json, sys, copy

def reduce(state, ev):
    s = copy.deepcopy(state)
    t = ev.get("t")
    d = ev.get("data", {})
    r = ev.get("result", {})
    if t == "create_char":
        c = d["character"]
        s["characters"][c["id"]] = c
    elif t == "update_char":
        cid = d["id"]
        s["characters"][cid].update(d["patch"])
    elif t == "gain_item":
        cid = d["id"]; item = d["item"]
        s["characters"][cid].setdefault("inventory", []).append(item)
    elif t == "lose_item":
        cid = d["id"]; item = d["item"]
        inv = s["characters"][cid].get("inventory", [])
        if item in inv: inv.remove(item)
    elif t == "damage":
        cid = d["id"]; amt = r.get("amount", d.get("amount", 0))
        s["characters"][cid]["hp"]["current"] = max(
            0, s["characters"][cid]["hp"]["current"] - amt)
    elif t == "heal":
        cid = d["id"]; amt = r.get("amount", d.get("amount", 0))
        mx = s["characters"][cid]["hp"]["max"]
        s["characters"][cid]["hp"]["current"] = min(
            mx, s["characters"][cid]["hp"]["current"] + amt)
    return s

if __name__ == "__main__":
    sess = json.load(sys.stdin)  # session JSON
    state = {"characters": {}}
    for ev in sess["events"]:
        state = reduce(state, ev)
    print(json.dumps(state, indent=2))
