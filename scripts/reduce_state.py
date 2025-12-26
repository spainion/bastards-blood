import copy
import json
import sys

def reduce(state, ev):
    s = copy.deepcopy(state)
    t = ev.get("t")
    d = ev.get("data", {})
    r = ev.get("result", {})

    def require_keys(obj, keys, ctx):
        missing = [k for k in keys if k not in obj]
        if missing:
            raise KeyError(f"{ctx} missing keys: {', '.join(missing)}")

    def ensure_char(cid):
        if cid not in s["characters"]:
            raise KeyError(f"unknown character id {cid}")
        return s["characters"][cid]

    def get_amount():
        return r.get("amount", d.get("amount", 0))

    require_keys(ev, ["id", "ts", "t"], "event")
    if t == "create_char":
        require_keys(d, ["character"], "create_char data")
        c = d["character"]
        s["characters"][c["id"]] = c
    elif t == "update_char":
        require_keys(d, ["id", "patch"], "update_char data")
        cid = d["id"]
        ensure_char(cid).update(d["patch"])
    elif t == "gain_item":
        require_keys(d, ["id", "item"], "gain_item data")
        cid = d["id"]
        item = d["item"]
        ensure_char(cid).setdefault("inventory", []).append(item)
    elif t == "lose_item":
        require_keys(d, ["id", "item"], "lose_item data")
        cid = d["id"]
        item = d["item"]
        inv = ensure_char(cid).get("inventory", [])
        # remove a single instance if present
        if item in inv:
            inv.remove(item)
    elif t == "damage":
        require_keys(d, ["id"], "damage data")
        cid = d["id"]
        amt = get_amount()
        hp = ensure_char(cid).get("hp", {})
        require_keys(hp, ["current"], f"hp for {cid}")
        hp["current"] = max(0, hp["current"] - amt)
    elif t == "heal":
        require_keys(d, ["id"], "heal data")
        cid = d["id"]
        amt = get_amount()
        hp = ensure_char(cid).get("hp", {})
        require_keys(hp, ["max", "current"], f"hp for {cid}")
        hp["current"] = min(hp["max"], hp["current"] + amt)
    return s

if __name__ == "__main__":
    sess = json.load(sys.stdin)  # session JSON with id, campaign, events[]
    for key in ("id", "campaign", "events"):
        if key not in sess:
            raise KeyError(f"session missing {key}")
    state = {"characters": {}}
    for ev in sess["events"]:
        state = reduce(state, ev)
    print(json.dumps(state, indent=2))
