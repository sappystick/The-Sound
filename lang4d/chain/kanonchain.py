#!/usr/bin/env python3
"""KANON CHAIN: a prototype ledger where every transaction is a speakable, sealed, error-correctable KANON program.

What it is: a single-process prototype of the EXECUTION and DATA layer (accounts, signed transactions, blocks, state roots,
replay validation). What it is not: a network. There is one sequencer and no peer-to-peer consensus; in the design
(CHAIN.md) consensus and security are borrowed from an established chain, not reinvented.

Features carried over from KANON:
  speakable addresses   20-byte account ids written as 13 KANON syllables + 5 Reed-Solomon words, said in English skin
                        words; up to 2 misheard words are repaired
  transactions = verses the human-readable form IS the executable form; the wallet can read it aloud (readback)
  gas known in advance  the KANON-FLIGHT static checker bounds steps BEFORE execution; the bound is the gas charged
  exact arithmetic      chain profile: every value must stay an integer below 2^53, so results are bit-identical on any
                        machine (floating-point maths functions are not)
  works as native       a work = one source; its id is the hash; its contract verses (::tako shares, ::paga payout) are
  objects               executed by the chain when revenue arrives; ownership transfers; statistics come from an oracle
Usage: python3 kanonchain.py   (runs the demonstration and tests)"""
import hashlib, json, os, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.dirname(HERE); sys.path.insert(0, L); sys.path.insert(0, os.path.join(L, "fields"))
import kanon as K, skins as S, profile as PF
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
def H(b): return hashlib.sha256(b).hexdigest()
def canon_json(x): return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
# ------------------------------------------------------------------ speakable addresses
NSYL = 13      # 20 bytes = 160 bits < 84^13 (about 1.04e25 > 1.46e48? no) -> use 26 syllables; computed below
def _bytes_to_syl(b, n):
    x = int.from_bytes(b, "big"); out = []
    for _ in range(n): out.append(x % 84); x //= 84
    assert x == 0; return out[::-1]
def _syl_to_bytes(s, nbytes):
    x = 0
    for v in s: x = x * 84 + v
    return x.to_bytes(nbytes, "big")
ADDR_BYTES = 10; ADDR_SYL = 13           # 80-bit account ids (84^13 > 2^80); a production design would use 20+ bytes
def address_of(pub_raw): return hashlib.sha256(pub_raw).digest()[:ADDR_BYTES]
def speak_address(addr):
    syl = _bytes_to_syl(addr, ADDR_SYL); par = K.rs_parity(syl)
    words = [K.CONS[v // 7] + K.VOWELS[v % 7] for v in syl] + [K._pword(p) for p in par]
    return "-".join(words[:ADDR_SYL]) + " =" + "-".join(words[ADDR_SYL:])
def hear_address(text):
    """Accept the canonical form or English skin words; repair up to 2 wrong words. -> (address bytes, words fixed)."""
    body, tail = text.split("=", 1)
    words = [x for t in text.replace("=", " ").split() for x in t.split("-")]
    skin = all(x in S.EN_DEC for x in words)       # a skin word can also be a valid KANON spelling (tea, no), so pick ONE mode
    def cell(w): return S.EN_DEC[w].lstrip("_") if skin else w
    bw = [cell(w) for w in body.replace(" ", "-").split("-") if w]
    tt = tail.split()
    if not skin: tw = [x for t in tt for x in t.split("-")]                                          # canonical: pe-te-bi-...
    else: tw = ["".join(cell(x) for x in t.split("-")) for t in tt]                                 # skin: pet tell bay-at ...
    syl = [K.CONS.index(w[0]) * 7 + K.VOWELS.index(w[1]) if len(w) == 2 and w[0] in K.CONS and w[1] in K.VOWELS else 0 for w in bw]
    par = [K._pval(w) or 0 for w in tw]
    fixed, n = K.rs_correct(par, syl)
    if fixed is None: raise ValueError("address cannot be repaired: ask the speaker to repeat it")
    return _syl_to_bytes(fixed, ADDR_BYTES), n
def skin_address(addr):
    a = speak_address(addr); body, tail = a.split(" =")
    return " ".join(S.EN_ENC[w] for w in body.split("-")) + " check " + " ".join("-".join(S._word(w, S.EN_ENC)) for w in tail.split("-"))
# ------------------------------------------------------------------ keys and transactions
class Wallet:
    def __init__(self, name):
        self.name = name; self.sk = Ed25519PrivateKey.generate()
        self.pub = self.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw); self.addr = address_of(self.pub)
    def sign(self, tx):
        tx = dict(tx, sender=self.addr.hex(), pub=self.pub.hex()); body = canon_json({k: v for k, v in tx.items() if k != "sig"})
        tx["sig"] = self.sk.sign(body).hex(); tx["hash"] = H(body); return tx
DEC = "zero one two three four five six seven eight nine".split()
def money(n): return " ".join(DEC[int(c)] for c in str(n)) + f" ({n})"     # amounts are read in decimal: base twelve is for programs, not money
def readback(tx):
    """What the wallet says aloud before signing: the transaction in English skin words."""
    k = tx["kind"]
    if k == "transfer": return f"pay {money(tx['amount'])} to {skin_address(bytes.fromhex(tx['to']))}"
    if k == "call": return "run " + S.to_skin(tx["source"])
    if k == "pay_work": return f"pay {money(tx['amount'])} into the work sealed {tx.get('seal', '')}"
    return k.replace("_", " ")
# ------------------------------------------------------------------ the exact-integer VM profile
LIMIT = 2 ** 53
class ChainVM(K.VM):
    def op(self, *a, **kw): super().op(*a, **kw); self.exact()
    def call(self, *a, **kw): super().call(*a, **kw); self.exact()      # library words are checked too
    def exact(self):
        for v, xs in self.P.items():
            for x in xs:
                if x != int(x) or abs(x) >= LIMIT: raise ArithmeticError(f"plane {v} holds {x}: the chain allows exact integers only")
def run_pure(source, gas_limit):
    """Static gas bound first, then exact execution. -> (vm, gas_used)."""
    rep = PF.analyse(source, mem_limit=4096)
    hard = [i for i in rep["issues"] if i[0] in ("F1", "F2", "F4")]
    if hard: raise ValueError("rejected before execution: " + "; ".join(m for _, m in hard))
    gas = rep["worst_case_steps"] + 10
    if gas > gas_limit: raise ValueError(f"static bound {gas} exceeds gas limit {gas_limit}")
    vm = ChainVM(); vm.fuel = gas_limit; vm.run(source); return vm, gas
# ------------------------------------------------------------------ the chain
class Chain:
    def __init__(self, genesis_balances, oracle):
        self.state = dict(balances={a.hex(): v for a, v in genesis_balances.items()}, nonces={}, works={}, oracle=oracle.hex())
        self.blocks = [dict(height=0, prev="0" * 64, txs=[], state_root=self.root())]; self.pending = []; self.receipts = {}
    def root(self): return H(canon_json(self.state))
    def submit(self, tx): self.pending.append(tx)
    def verify_sig(self, tx):
        pub = bytes.fromhex(tx["pub"]); assert address_of(pub).hex() == tx["sender"], "key does not match sender"
        Ed25519PublicKey.from_public_bytes(pub).verify(bytes.fromhex(tx["sig"]), canon_json({k: v for k, v in tx.items() if k not in ("sig", "hash")}))
    def apply(self, st, tx):
        self.verify_sig(tx); s = tx["sender"]; nonce = st["nonces"].get(s, 0)
        if tx["nonce"] != nonce: raise ValueError("bad nonce")
        st["nonces"][s] = nonce + 1; bal = st["balances"]; k = tx["kind"]
        if k == "transfer":
            if bal.get(s, 0) < tx["amount"]: raise ValueError("insufficient balance")
            bal[s] -= tx["amount"]; bal[tx["to"]] = bal.get(tx["to"], 0) + tx["amount"]; return dict(ok=True)
        if k == "call":
            vm, gas = run_pure(tx["source"], tx.get("gas", 5000)); return dict(ok=True, gas=gas, i=vm.P["i"], out=[str(o) for o in vm.out])
        if k == "register_work":
            src = K.norm_text(tx["source"]); wid = H(src.encode())
            if wid in st["works"]: raise ValueError("work already registered")
            vm, gas = run_pure(src + " | :tako", 5000); shares = [int(x) for x in vm.P["o"]]
            if sum(shares) != 100 or len(shares) != len(tx["payees"]): raise ValueError(f"contract shares {shares} must sum to 100 and match {len(tx['payees'])} payees")
            st["works"][wid] = dict(owner=s, source=src, seal=K.checksum_word(src), payees=tx["payees"], shares=shares, plays=0, revenue=0)
            return dict(ok=True, work=wid, seal=st["works"][wid]["seal"], gas=gas)
        if k == "pay_work":
            w = st["works"][tx["work"]]; amt = tx["amount"]
            if bal.get(s, 0) < amt: raise ValueError("insufficient balance")
            vm, gas = run_pure(w["source"] + f" | ka #{K.to12(amt)} | :paga", 5000)   # the work's own payout rule, exactly
            pay = [int(x) for x in vm.P["i"]]
            if sum(pay) != amt or len(pay) != len(w["payees"]): raise ValueError(f"payout {pay} does not distribute {amt} exactly")
            bal[s] -= amt
            for who, p in zip(w["payees"], pay): bal[who] = bal.get(who, 0) + p
            w["revenue"] += amt; return dict(ok=True, payout=pay, gas=gas)
        if k == "report_plays":
            if s != st["oracle"]: raise ValueError("only the oracle reports plays")
            st["works"][tx["work"]]["plays"] += tx["plays"]; return dict(ok=True)
        if k == "transfer_work":
            w = st["works"][tx["work"]]
            if w["owner"] != s: raise ValueError("only the owner transfers a work")
            w["owner"] = tx["to"]; return dict(ok=True)
        raise ValueError("unknown kind")
    def seal_block(self):
        st = copy.deepcopy(self.state); txs, rec = [], {}
        for tx in self.pending:
            trial = copy.deepcopy(st)
            try: r = self.apply(trial, tx); st = trial
            except Exception as e: r = dict(ok=False, error=str(e)); st["nonces"][tx["sender"]] = st["nonces"].get(tx["sender"], 0) + (1 if tx.get("nonce") == st["nonces"].get(tx["sender"], 0) else 0)
            txs.append(tx); rec[tx["hash"]] = r
        self.state = st; self.pending = []; self.receipts.update(rec)
        b = dict(height=len(self.blocks), prev=H(canon_json(self.blocks[-1])), txs=txs, state_root=self.root()); self.blocks.append(b); return b, rec
def replay(blocks, genesis_balances, oracle):
    """Any node can recompute every state root from genesis; returns the first height that disagrees, or None."""
    c = Chain(genesis_balances, oracle)
    for b in blocks[1:]:
        if b["prev"] != H(canon_json(c.blocks[-1])): return b["height"]
        for tx in b["txs"]: c.submit(tx)
        nb, _ = c.seal_block()
        if nb["state_root"] != b["state_root"]: return b["height"]
    return None
# ------------------------------------------------------------------ demonstration and tests
if __name__ == "__main__":
    out = {}
    A, P, Lb, F, O = (Wallet(n) for n in ("artist", "producer", "label", "fan", "oracle"))
    gen = {F.addr: 10000, A.addr: 100}
    ch = Chain(gen, O.addr); nonce = {w.name: 0 for w in (A, P, Lb, F, O)}
    def tx(w, **kw): t = w.sign(dict(kw, nonce=nonce[w.name])); nonce[w.name] += 1; return t
    # 1. speakable addresses, with repair
    sa = speak_address(F.addr); sk = skin_address(F.addr); words = sk.split()
    damaged = list(words); damaged[2] = "moon" if damaged[2] != "moon" else "cat"; damaged[7] = "tea" if damaged[7] != "tea" else "bee"
    got, n = hear_address(" ".join(damaged[:13]) + " =" + " ".join(damaged[14:]))
    out["address"] = dict(canonical=sa, english=sk, two_words_misheard=" ".join(damaged), recovered=got == F.addr, words_repaired=n)
    # 2. a work: register, pay, report, transfer
    src = open(os.path.join(L, "work", "work.kn")).read()
    t_reg = tx(A, kind="register_work", source=src, payees=[A.addr.hex(), P.addr.hex(), Lb.addr.hex()])
    t_pay = tx(F, kind="pay_work", work=H(K.norm_text(src).encode()), amount=5000)
    t_bad = tx(F, kind="pay_work", work=H(K.norm_text(src).encode()), amount=1001)
    t_rep = tx(O, kind="report_plays", work=H(K.norm_text(src).encode()), plays=1000)
    t_fake = tx(F, kind="report_plays", work=H(K.norm_text(src).encode()), plays=99999)
    t_call = tx(F, kind="call", source="ki #70 | ka #30 | bia | :kagi | :dasa", gas=500)
    t_kegi = tx(F, kind="call", source="ki #70 | ka #30 | :kegi | :dasa", gas=500)
    t_loop = tx(F, kind="call", source="ki #5 | li pi #2", gas=500)
    t_tr = tx(F, kind="transfer", to=A.addr.hex(), amount=250)
    for t in (t_reg, t_pay, t_bad, t_rep, t_fake, t_call, t_kegi, t_loop, t_tr): ch.submit(t)
    b1, rec = ch.seal_block()
    names = ["register the work", "fan pays 5000 into the work", "fan pays 1001 (the payout would need fractions)", "oracle reports 1000 plays",
             "fan pretends to be the oracle", "pure computation: gcd(84, 36) with the built-in :kagi", "the same gcd with the KANON-written :kegi (a while-loop)", "unbounded loop", "fan transfers 250 to the artist"]
    out["block1"] = {n: rec[t["hash"]] for n, t in zip(names, (t_reg, t_pay, t_bad, t_rep, t_fake, t_call, t_kegi, t_loop, t_tr))}
    t_own = tx(A, kind="transfer_work", work=H(K.norm_text(src).encode()), to=Lb.addr.hex()); ch.submit(t_own); b2, rec2 = ch.seal_block()
    out["block2"] = {"artist sells the work to the label": rec2[t_own["hash"]]}
    w = ch.state["works"][H(K.norm_text(src).encode())]
    out["work_state"] = dict(seal=w["seal"], owner_is_label=w["owner"] == Lb.addr.hex(), plays=w["plays"], revenue=w["revenue"], shares=w["shares"])
    out["balances"] = {nm: ch.state["balances"].get(wl.addr.hex(), 0) for nm, wl in (("artist", A), ("producer", P), ("label", Lb), ("fan", F))}
    out["readback_examples"] = [readback(t_tr), readback(dict(t_pay, seal=w["seal"])), readback(t_call)]
    # 3. any node can replay; a tampered block is detected
    out["replay_clean"] = replay(ch.blocks, gen, O.addr) is None
    forged = copy.deepcopy(ch.blocks); forged[1]["txs"][1]["amount"] = 50
    out["replay_after_tampering_detected_at_height"] = replay(forged, gen, O.addr)
    json.dump(out, open(os.path.join(HERE, "demo_results.json"), "w"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
