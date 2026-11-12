# A KANON blockchain: approach, build plan, prototype and an honest verdict (round 70)

## 1. Verdict first

**Another layer-1 chain that competes on consensus, speed or fees would not be groundbreaking.** There are hundreds already. Security has to be bootstrapped with a validator set and capital, and that is where new chains usually fail. KANON brings nothing new to consensus.

**What would be new is the human layer, which no chain has:**
- transactions and contracts that are **speakable, sealed, error-corrected and statically bounded programs**, and that can travel over a **phone call**;
- creative **works as native objects**: one source from which song, video, contract and statistics are rendered and checked.

So the best approach is to **borrow security and own the experience**: a KANON execution layer (an app-specific rollup) that settles to an established chain, preceded by a cheap phase that tests demand on an existing chain.

## 2. What already exists, and what does not

| Feature | Closest existing system | Gap KANON fills |
|---|---|---|
| A contract language with no unbounded loops and costs known in advance | **Clarity** (Stacks) is decidable; **TEAL** (Algorand) is bounded; **Michelson** (Tezos) is formally specified | None of them can be spoken, heard or error-corrected |
| Human-readable addresses | **ENS** names; **BIP39** seed words | ENS needs a registry and has no correction; BIP39 detects errors but cannot repair them |
| Art generated from an on-chain program | **Art Blocks** (generative art from a hash) | One medium only; the contract is separate |
| Music NFTs and royalty splits | Royal, Sound.xyz; **0xSplits** | The split, the song and the video are separate artefacts |
| Voice access to money | USSD mobile money (M-Pesa) | Not verifiable, not programmable, not on a ledger |

**The novel combination:**
1. One alphabet that is at once the program, the speech, the modem symbols, the error-correcting code and the seal.
2. Signing by **readback**: the wallet says the transaction aloud and the user confirms it.
3. Transactions that survive a **GSM phone call** (40 of 40 in round 68's tests).
4. A tiny exact-integer VM whose cost is proven before it runs.
5. Works as native, multi-channel objects.

I know of no chain that offers 1–3, and none that combines all five.

## 3. Architecture

```
  people: voice / phone call / screen / seal          machines: wallets, phones, feature phones, IoT
            │  English (or any) word skin, readback        │  tone codec (studio or phone channel) + Reed–Solomon
            ▼                                              ▼
  ┌──────────────────────── KANON EXECUTION LAYER (app rollup) ─────────────────────────┐
  │ accounts: speakable addresses (13 syllables + 5 repair words)                       │
  │ transactions: signed KANON verses; static checker gives gas BEFORE execution        │
  │ VM: KANON chain profile, exact integers only (identical results on every machine)   │
  │ native objects: WORKS (source hash, seal, payees, shares, plays, revenue, owner)    │
  │ library: Canon words with declared gas costs; chain words for state                 │
  └───────────────┬──────────────────────────────────────────────┬──────────────────────┘
                  │ batches + state roots + proofs               │ oracle feeds (plays, prices)
                  ▼                                              ▼
       SETTLEMENT AND SECURITY: an established chain (Ethereum rollup stack, or a Cosmos app-chain
       with shared security); data availability from that chain or a DA layer
```

**A strategic point: proofs.** The KANON VM has 12 operations, list-valued planes and integer arithmetic. A tiny, fully deterministic instruction set is cheap to prove in zero knowledge, much cheaper than the EVM. A KANON rollup could post **validity proofs**: every block comes with a proof that every spoken program ran correctly. This makes the chain fast to verify and is a credible technical edge.

## 4. How each feature integrates

| KANON feature | On-chain role | Built in the prototype? |
|---|---|---|
| Speakable addresses + Reed–Solomon | Account ids said as words; 2 misheard words repaired | **Yes:** 200 of 200 repaired with 2 wrong words |
| Readback | The wallet speaks the transaction before signing; amounts in decimal | **Yes:** "pay two five zero (250) to cat heat deep lab …" |
| Static checker (KANON-FLIGHT) | Rejects unbounded loops and recursion; sets gas before execution | **Yes:** the unbounded loop and the while-loop gcd were rejected before running |
| Exact-integer profile | Determinism across machines | **Yes:** a 1,001 payout needing 500.5 is refused as non-exact |
| Works as native objects | Register, pay, report plays, transfer ownership | **Yes:** 5,000 paid out 2,500 / 1,500 / 1,000 by the work's own `::paga` |
| Oracle | Only the oracle can report statistics | **Yes:** an impostor's report was rejected |
| Replay validation | Any node recomputes state roots from genesis | **Yes:** clean replay matches; a tampered block is detected at height 1 |
| Phone-channel transactions | Submit a signed verse over a voice call | Codec ready (GSM 40 of 40); not wired to the chain yet |
| Deterministic rendering of works | Song and video hashes checkable by anyone | Ready for audio and frames (round 69). Video needs pinned fonts and renderer versions for cross-machine identity. |
| Seals | Visual confirmation of addresses, transactions and works | Ready; not shown in a wallet yet |
| Validity proofs | Proof per block | No |
| Networking and consensus | Peers, sequencer rotation, bridge | No (borrowed in the design) |

## 5. Problems the prototype surfaced

These are the reason to build before claiming:
1. **Floating point cannot be on a chain.** The KANON VM uses floats; maths functions differ between machines. The chain profile now allows exact integers only.
2. **Library words need real gas costs.** A Canon call is charged 1 step, but `:kapi` can list primes up to a million. Each built-in needs a declared cost function.
3. **The while-loop prelude is not chain-legal.** `:kegi` (Euclid with a while-loop) is rejected; the chain needs bounded versions of the prelude. The built-in `:kagi` works.
4. **Base-twelve money is unusable.** Programs may stay base twelve, but amounts must be read in decimal.
5. **Skin words collide with KANON spellings.** "tea" and "no" are also valid syllable words, so input must be parsed in one declared mode: all skin or all canonical.
6. **Voice is not authentication.** Spoken readback confirms *what* is signed, but the signature still comes from a key. Voice alone must never authorise a payment. Voice spoofing and attacks on speech recognition are real threats.

## 6. Build plan

| Phase | Time | Build | Go/no-go evidence |
|---|---|---|---|
| **0. Prove demand on an existing chain** | 0–3 months | A wallet with speakable addresses, readback signing and seals; a works-registry contract (source hash, payees, shares) on an established chain; KANON-FLIGHT → contract-language transpiler for splits | Do people prefer readback signing? Error rates against hex addresses? Do artists register works? |
| **1. KANON rollup devnet** | 3–12 months | Port the VM to Rust with the integer profile and declared costs; sequencer; bridge to the settlement chain; fraud proofs first, then validity proofs; phone-channel submission gateway | Determinism across 3 implementations (Python, JS, Rust); a cost model; a security audit |
| **2. Media and voice access** | 12–24 months | Deterministic renderer spec (pinned fonts and codecs); oracle network for plays; royalty streams; a feature-phone gateway (call a number, speak or play a transaction, hear the readback, confirm with a PIN or key) | Pilots: an artist collective, and a community using feature phones |
| **3. Mainnet or not** | 24+ months | Only if Phases 0–2 show real use | Users, works registered, value settled, incident record |

## 7. Is this a valid groundbreaking aim?

**Yes, for two specific propositions:**
1. **Voice-native, error-corrected, readback-signed transactions.** These reach people and situations without smartphones or screens, and make every transaction human-checkable. I know of no ledger that does this. The phone-channel result (GSM 40 of 40) makes it technically credible.
2. **Works as single-source, multi-channel, verifiable objects:** song, video, lyrics, contract and statistics from one program and one hash.

**No, if the aim is to out-compete existing chains on general smart contracts, throughput or DeFi.** KANON brings nothing there, and a new consensus network would spend its energy on problems others have solved.

**Main risks:**
- **Regulation:** money transmission and securities law for royalty tokens.
- **Security:** of the voice channel, and audits.
- **Oracles:** they must be trusted for play counts.
- **Adoption:** wallets and artists must choose it.
- **Distraction:** chasing an independent layer-1 too early.

## 8. Run the prototype

```bash
python3 lang4d/chain/kanonchain.py
```

It prints and saves `lang4d/chain/demo_results.json`: speakable addresses with repair, a work registered and paid by its own contract, rejected bad transactions, ownership transfer, readback text, replay and tamper detection.

It is single-process, with one sequencer and no network: a test of the execution and data design, not a deployable chain.
