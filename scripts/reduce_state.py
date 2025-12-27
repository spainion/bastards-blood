import json, sys, copy

def reduce(state, ev):
    s = copy.deepcopy(state)
    t = ev.get("t")
    d = ev.get("data", {})
    r = ev.get("result", {})
    if t == "create_char":
        c = d.get("character")
        if c and "id" in c:
            s["characters"][c["id"]] = c
    elif t == "update_char":
        cid = d.get("id")
        patch = d.get("patch", {})
        if cid in s["characters"] and isinstance(patch, dict):
            allowed = {"id", "name", "class", "lvl", "stats", "hp", "inventory", "tags", "notes"}
            filtered_patch = {k: v for k, v in patch.items() if k in allowed}
            if filtered_patch:
                s["characters"][cid].update(filtered_patch)
    elif t == "gain_item":
        cid = d.get("id")
        item = d.get("item")
        if cid in s["characters"] and item is not None:
            s["characters"][cid].setdefault("inventory", []).append(item)
    elif t == "lose_item":
        cid = d.get("id")
        item = d.get("item")
        if cid in s["characters"] and item is not None:
            inv = s["characters"][cid].setdefault("inventory", [])
            if item in inv: inv.remove(item)
    elif t == "damage":
        cid = d.get("id")
        amt = r.get("amount", d.get("amount", 0))
        char = s["characters"].get(cid) if cid else None
        if char:
            hp = char.get("hp", {})
            if "current" in hp:
                hp["current"] = max(0, hp.get("current", 0) - amt)
                char["hp"] = hp
                s["characters"][cid] = char
    elif t == "heal":
        cid = d.get("id")
        amt = r.get("amount", d.get("amount", 0))
        char = s["characters"].get(cid) if cid else None
        if char:
            hp = char.get("hp", {})
            if "current" in hp and "max" in hp:
                hp["current"] = min(hp["max"], hp.get("current", 0) + amt)
                char["hp"] = hp
                s["characters"][cid] = char
    return s

if __name__ == "__main__":
    sess = json.load(sys.stdin)  # session JSON
    state = {"characters": {}}
    for ev in sess.get("events", []):
        state = reduce(state, ev)
    print(json.dumps(state, indent=2))
