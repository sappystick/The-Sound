// KANON v0.2 interpreter in JavaScript: the same language as kanon.py (parity-tested by course.py).
// Runs in a browser or in node. No dependencies.
(function (root) {
  const VOWELS = "aeyiouw", CONS = "ktpbdglmnrsh", DIGITS = "0123456789te";
  const RATIO = {a: 4/3, e: 32/27, y: 256/243, i: 1, o: 8/9, u: 64/81, w: 0.75};
  const F0 = 154.2, FUEL = 200000, MAXLEN = 65536;
  const isWord = w => {
    if (w.length < 2) return false;
    for (let j = 0; j < w.length - w.length % 2; j++) if (j % 2 ? !VOWELS.includes(w[j]) : !CONS.includes(w[j])) return false;
    return w.length % 2 === 0 || VOWELS.includes(w[w.length - 1]);
  };
  const TOKEN = /\s*(\|)|\s*(=[a-z]+)|\s*(::?)([a-z]*)([!?]*)|\s*(~?)([a-z]+)([!?]*)|\s*(#[0-9te]+)/y;
  function lex(src) {
    const out = []; src = src.replace(/\n/g, " "); let pos = 0;
    while (pos < src.length) {
      if (!src.slice(pos).trim()) break;
      TOKEN.lastIndex = pos; const m = TOKEN.exec(src);
      if (!m || TOKEN.lastIndex === pos) throw new SyntaxError(`cannot read "${src.slice(pos, pos + 12)}"`);
      pos = TOKEN.lastIndex;
      if (m[1]) out.push(["bar"]);
      else if (m[2]) out.push(["sum", m[2].slice(1)]);
      else if (m[3]) {
        if (m[3] === "::") out.push(m[4] ? ["def", m[4]] : ["end"]);
        else { if (!isWord(m[4])) throw new SyntaxError(`bad name "${m[4]}"`); out.push(["call", m[4], {urgent: m[5].includes("!"), guard: m[5].includes("?"), sandbox: false}]); }
      } else if (m[7]) {
        if (!isWord(m[7])) throw new SyntaxError(`bad word "${m[7]}": syllables are consonant + vowel, with an optional final vowel`);
        out.push(["word", m[7], {urgent: m[8].includes("!"), guard: m[8].includes("?"), sandbox: m[6] === "~"}]);
      } else { let v = 0; for (const ch of m[9].slice(1)) v = v * 12 + DIGITS.indexOf(ch); out.push(["num", v]); }
    }
    return out;
  }
  function parse(src) {
    src = src.replace(/=[^|]*/g, "");   // checksum and error-correction tails are for the channel, not the machine
    const main = [], defs = {}; let cur = null, verse = [];
    const close = () => { if (verse.length) (cur ? defs[cur] : main).push(verse); verse = []; };
    for (const t of lex(src)) {
      if (t[0] === "bar") close();
      else if (t[0] === "def") { close(); cur = t[1]; defs[cur] = []; }
      else if (t[0] === "end") { close(); cur = null; }
      else if (t[0] === "num") { if (verse.length) verse[verse.length - 1].num = t[1]; else verse.push({kind: "word", word: "ki", num: t[1], urgent: false, guard: false, sandbox: false}); }
      else if (t[0] === "sum") {}
      else verse.push(Object.assign({kind: t[0], word: t[1], num: null}, t[2]));
    }
    close(); return [main, defs];
  }
  function bindLoops(items) {
    const out = []; let i = 0;
    while (i < items.length) { const it = items[i];
      if (it.kind === "word" && it.word[0] === "l" && i + 1 < items.length) { out.push(Object.assign({}, it, {body: items[i + 1]})); i += 2; }
      else { out.push(it); i++; } }
    return out;
  }
  function schedule(items) {
    const out = [], rest = []; for (const it of items) (it.urgent ? out : rest).push(it);
    const n = rest.length; for (let k = 0; k < Math.floor(n / 2); k++) out.push(rest[k], rest[n - 1 - k]);
    if (n % 2) out.push(rest[(n - 1) / 2]); return out;
  }
  function ring(seq) { const n = seq.length, order = [], pos = new Array(n);
    for (let k = 0; k < Math.floor(n / 2); k++) order.push(k, n - 1 - k); if (n % 2) order.push((n - 1) / 2);
    order.forEach((slot, j) => pos[slot] = seq[j]); return pos; }
  const fold = x => { x = Math.abs(x) || 1; while (x >= 2.5) x /= 2; while (x < 0.625) x *= 2; return x; };
  const toint = x => Math.trunc(Math.round(x * 1e9) / 1e9);
  const truthy = p => p.length > 0 && p[p.length - 1] > 0;
  const fmod = (a, b) => a % b;   // same sign rule as Python's math.fmod
  const last = p => { if (!p.length) throw new RangeError("list index out of range"); return p[p.length - 1]; };
  const sum = p => {   // Neumaier compensated summation, as Python 3.12+ sum() does for floats
    let s = 0, c = 0; for (const x of p) { const t = s + x; c += Math.abs(s) >= Math.abs(x) ? (s - t) + x : (x - t) + s; s = t; } return s + c; };
  const g = n => { const out = []; for (let k = 1; k <= n; k++) out.push(k); return out; };
  const gcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) [a, b] = [b, a % b]; return a; };
  const primes = n => { const s = new Array(n + 1).fill(true); s[0] = false; if (n >= 1) s[1] = false;
    for (let p = 2; p * p <= n; p++) if (s[p]) for (let q = p * p; q <= n; q += p) s[q] = false; return s.map((v, k) => v ? k : -1).filter(k => k >= 0); };
  const GREEK = [[900,"ϡ"],[800,"ω"],[700,"ψ"],[600,"χ"],[500,"φ"],[400,"υ"],[300,"τ"],[200,"σ"],[100,"ρ"],[90,"ϙ"],[80,"π"],[70,"ο"],[60,"ξ"],[50,"ν"],[40,"μ"],[30,"λ"],[20,"κ"],[10,"ι"],[9,"θ"],[8,"η"],[7,"ζ"],[6,"ϛ"],[5,"ε"],[4,"δ"],[3,"γ"],[2,"β"],[1,"α"]];
  const HEB = [[400,"ת"],[300,"ש"],[200,"ר"],[100,"ק"],[90,"צ"],[80,"פ"],[70,"ע"],[60,"ס"],[50,"נ"],[40,"מ"],[30,"ל"],[20,"כ"],[10,"י"],[9,"ט"],[8,"ח"],[7,"ז"],[6,"ו"],[5,"ה"],[4,"ד"],[3,"ג"],[2,"ב"],[1,"א"]];
  function numeral(n, table) { n = Math.trunc(n); let s = "";
    if (table === HEB) { while (n >= 400) { s += "ת"; n -= 400; }
      if (n % 100 === 15 || n % 100 === 16) { if (n >= 100) s += numeral(n - n % 100, table); return s + (n % 100 === 15 ? "טו" : "טז"); } }
    for (const [v, ch] of table) while (n >= v) { s += ch; n -= v; } return s + (table === GREEK ? "ʹ" : ""); }
  const fmt = x => { if (Number.isInteger(x)) return String(x); const s = x.toPrecision(6); return String(parseFloat(s)); };
  const modes = side => { const c = 343, set = new Set();
    for (let a = 0; a < 4; a++) for (let b = 0; b < 4; b++) for (let d = 0; d < 4; d++) if (a + b + d) set.add(Math.round(c / 2 * Math.sqrt(a*a + b*b + d*d) / side * 100) / 100);
    return [...set].sort((x, y) => x - y).slice(0, 7); };
  const CANON = {
    kamu: ["multiply: i ← i × a", vm => vm.set(vm.P.a.length === vm.P.i.length ? vm.P.i.map((x, k) => x * vm.P.a[k]) : vm.P.i.map(x => x * (vm.P.a.length ? last(vm.P.a) : 1)))],
    kade: ["divide: i ← i ÷ a", vm => vm.set(vm.P.i.map(x => x / (last(vm.P.a) || NaN)))],
    kagi: ["greatest common divisor of i", vm => vm.set(vm.P.i.length ? [vm.P.i.map(Math.trunc).reduce(gcd)] : [])],
    kapi: ["primes up to i's last value", (vm, v) => { const n = Math.trunc(vm.P.i.length ? last(vm.P.i) : (v || 0)); if (n > 1e6) throw new RangeError("primes are listed up to 1,000,000"); vm.set(primes(n)); }],
    kasu: ["square root", vm => vm.set(vm.P.i.map(Math.sqrt))],
    kapo: ["power: i ^ a", vm => vm.set(vm.P.i.map(x => Math.pow(x, vm.P.a.length ? last(vm.P.a) : 2)))],
    kaha: ["factorial", vm => { let f = 1; for (let k = 2; k <= Math.trunc(last(vm.P.i)); k++) f *= k; vm.set([f]); }],
    kamo: ["product of all values", vm => vm.set([vm.P.i.reduce((p, x) => p * x, 1)])],
    tame: ["mean", vm => vm.set([sum(vm.P.i) / vm.P.i.length])],
    tado: ["median", vm => { const s = [...vm.P.i].sort((a, b) => a - b), n = s.length; vm.set([n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2]); }],
    tasi: ["standard deviation", vm => { const m = sum(vm.P.i) / vm.P.i.length; vm.set([Math.sqrt(sum(vm.P.i.map(x => (x - m) ** 2)) / vm.P.i.length)]); }],
    tami: ["minimum", vm => vm.set([Math.min(...vm.P.i)])],
    tamo: ["maximum", vm => vm.set([Math.max(...vm.P.i)])],
    taso: ["sort ascending", vm => vm.set([...vm.P.i].sort((a, b) => a - b))],
    papi: ["π", vm => vm.set([Math.PI])],
    pagu: ["the golden ratio", vm => vm.set([(1 + Math.sqrt(5)) / 2])],
    pari: ["interior angle of a regular polygon with i sides", vm => vm.set(vm.P.i.map(x => 180 * (x - 2) / x))],
    paso: ["star polygon {n/k}: visiting order (i = n, a = k)", vm => { const n = Math.trunc(last(vm.P.i)), k = Math.trunc(vm.P.a.length ? last(vm.P.a) : 2); vm.set(g(Math.min(n, MAXLEN + 1)).map(j => ((j - 1) * k) % n)); }],
    pamo: ["first seven resonances of a cube room of side i metres", vm => vm.set(modes(last(vm.P.i)))],
    pake: ["cubits to metres", vm => vm.set(vm.P.i.map(x => x * 0.5236))],
    bari: ["Fibonacci numbers up to i", vm => { const n = last(vm.P.i), s = [1, 1]; while (s[s.length - 1] + s[s.length - 2] <= n) s.push(s[s.length - 1] + s[s.length - 2]); vm.set(s.filter(x => x <= n)); }],
    basa: ["triangular numbers", vm => vm.set(g(Math.min(Math.trunc(last(vm.P.i)), MAXLEN + 1)).map(k => k * (k + 1) / 2))],
    bake: ["running sum", vm => { let s = 0; vm.set(vm.P.i.map(x => s += x)); }],
    bada: ["differences between neighbours", vm => vm.set(vm.P.i.slice(1).map((x, k) => x - vm.P.i[k]))],
    baro: ["distinct values", vm => vm.set([...new Set(vm.P.i)])],
    bato: ["take the first n values", (vm, v) => vm.set(vm.P.i.slice(0, Math.trunc(v || 3)))],
    baka: ["count of values", vm => vm.set([vm.P.i.length])],
    dasa: ["say i as numbers", vm => vm.say(vm.P.i.map(fmt).join(" "))],
    dagi: ["say i as Greek numerals", vm => vm.say(vm.P.i.map(x => numeral(x, GREEK)).join(" "))],
    dahe: ["say i as Hebrew numerals", vm => vm.say(vm.P.i.map(x => numeral(x, HEB)).join(" "))],
    dami: ["sing i as a melody", vm => vm.events.push(["melody", vm.P.i.map(fold)])],
    lane: ["not", vm => vm.set(vm.P.i.map(x => x ? 0 : 1))],
    lake: ["equal: i == a", vm => vm.set([JSON.stringify(vm.P.i) === JSON.stringify(vm.P.a) ? 1 : 0])],
    lame: ["less: i < a", vm => vm.set([last(vm.P.i) < last(vm.P.a) ? 1 : 0])],
    lamo: ["more: i > a", vm => vm.set([last(vm.P.i) > last(vm.P.a) ? 1 : 0])],
    maro: ["the seven string ratios", vm => vm.set([...VOWELS].map(c => RATIO[c]))],
    mahe: ["ratios → Hz on the carrier", vm => vm.set(vm.P.i.map(x => x * F0))],
    maki: ["interval in cents from i[0]", vm => vm.set(vm.P.i.map(x => 1200 * Math.log2(x / vm.P.i[0])))],
    mapu: ["the Pythagorean comma in cents", vm => vm.set([1200 * Math.log2(Math.pow(3, 12) / Math.pow(2, 19))])],
    rado: ["planetary weekday of J2000 + i days (0 = Sunday)", vm => vm.set([((Math.trunc(2451545 + (vm.P.i.length ? last(vm.P.i) : 0) + 1.5) % 7) + 7) % 7])],
  };
  const PRELUDE = `
::kemu kua | kw #0 | lu :keso | kiw ::
::keso bwi nu #1 gw ::
::kegi la :keto ::
::keto kei kia kae mea ::
::kehi kyi | ko #1 | ly :keho | kio ::
::keho kio :kemu ny #1 koi kay ::`;
  class VM {
    constructor() { this.P = {}; for (const v of VOWELS) this.P[v] = []; this.events = []; this.out = []; this.trace = []; this.defs = {}; this.fuel = FUEL;
      Object.assign(this.defs, parse(PRELUDE)[1]); }
    set(xs) { if (xs.length > MAXLEN) throw new RangeError(`result of ${xs.length} values exceeds ${MAXLEN}`); xs = xs.map(Number); if (!xs.every(Number.isFinite)) throw new RangeError("not a finite number (division by zero or an empty input)"); this.P.i = xs; }
    say(t) { this.out.push(t); }
    run(src) { const [main, defs] = parse(src); Object.assign(this.defs, defs); for (const v of main) this.verse(v); return this; }
    verse(items) { for (const it of schedule(bindLoops(items))) this.item(it); }
    tick() { if (--this.fuel < 0) throw new Error("out of fuel (a loop that never ends?)"); }
    item(it) {
      this.tick();
      if (it.guard && !truthy(this.P.i)) { this.trace.push("skip " + it.word); return; }
      try {
        if (it.kind === "call") this.call(it.word, it.num);
        else if (it.body) this.loop(it);
        else this.word(it.word, it.num);
      } catch (e) { if (it.sandbox) this.trace.push(`~${it.word}: skipped (${e.message})`); else throw e; }
    }
    loop(it) { const plane = it.word[1];
      if (it.num !== null) for (let k = 0; k < toint(it.num); k++) this.item(it.body);
      else while (truthy(this.P[plane])) this.item(it.body); }
    call(name, val) { this.trace.push(":" + name);
      if (this.defs[name]) { for (const v of this.defs[name]) this.verse(v); }
      else if (CANON[name]) CANON[name][1](this, val);
      else throw new Error(`unknown name :${name}`); }
    word(w, val) {
      const syl = []; for (let j = 0; j < w.length - w.length % 2; j += 2) syl.push(w.slice(j, j + 2));
      const cad = w.length % 2 ? w[w.length - 1] : null, op = syl[0][0], head = syl[0][1];
      if (op === "d" && syl.length >= 2) { this.events.push(["melody", [...w].filter(c => VOWELS.includes(c)).map(c => RATIO[c])]); this.trace.push(w + " (song)"); return; }
      this.op(op, head, cad, val, cad !== null);
      for (const s of syl.slice(1)) { this.tick(); this.op(s[0], head, s[1], null, true); }
      this.trace.push(`${w}${val === null ? "" : " #" + val} → ${head} = [${this.P[head].slice(0, 8).map(fmt).join(", ")}]`);
    }
    op(op, head, src, val, explicit) {
      const P = this.P, H = P[head], S = src ? P[src] : H;
      switch (op) {
        case "s": { const n = val !== null ? toint(val) : (explicit && S.length ? toint(last(S)) : 7); if (n > MAXLEN) throw new RangeError(`stream of ${n} values exceeds ${MAXLEN}`); P[head] = g(n); break; }
        case "k": P[head] = val !== null ? [val] : (explicit ? [...S] : []); break;
        case "b": P[head] = H.concat(S); break;
        case "p": P[head] = H.map(x => x * (val !== null ? val : RATIO[src || "i"])); break;
        case "g": P[head] = [sum(S) + (val || 0)]; break;
        case "t": { const thr = val !== null ? val : (explicit && src !== head && S.length ? last(S) : (H.length ? sum(H) / H.length : 0)); P[head] = H.filter(x => x > thr); break; }
        case "n": if (val !== null) P[head] = H.map(x => x - val); else if (explicit && src !== head) { const d = S.length ? last(S) : 0; P[head] = H.map(x => x - d); } else P[head] = H.map(x => -x); break;
        case "r": if (val !== null && H.length) { const k = toint(val) % H.length; P[head] = H.slice(k).concat(H.slice(0, k)); } else P[head] = [...H].reverse(); break;
        case "m": if (val !== null) P[head] = H.map(x => val ? fmod(x, val) : x);
          else if (explicit && src !== head && S.length && last(S)) P[head] = H.map(x => fmod(x, last(S)));
          else { const t = RATIO[src || "i"], n = Math.max(1, H.length); P[head] = H.map((x, j) => x * Math.pow(t, (j + 1) / n)); } break;
        case "d": this.events.push(["melody", H.map(fold)]); this.out.push(H.map(fmt).join(" ")); break;
        case "h": if (explicit) P[head] = [S.length]; else this.events.push(["rest", (val || 2) * 0.1]); break;
      }
      if (P[head].length > MAXLEN) throw new RangeError(`plane ${head} would hold ${P[head].length} values (limit ${MAXLEN})`);
      if (!P[head].every(Number.isFinite)) throw new RangeError("not a finite number");
    }
  }
  // Reed-Solomon parity over GF(113), identical to kanon.py: five parity symbols per block of up to 100 symbols
  const GF = 113, ALPHA = 3, NSYM = 5, BLOCK = 100;
  const pmod = a => ((a % GF) + GF) % GF;
  const ppow = (b, e) => { let r = 1; b = pmod(b); while (e > 0) { if (e & 1) r = r * b % GF; b = b * b % GF; e >>= 1; } return r; };
  function rsGen(n) { let g = [1]; for (let j = 1; j <= n; j++) { const a = pmod(-ppow(ALPHA, j)), r = new Array(g.length + 1).fill(0);
    g.forEach((x, i) => { r[i] = pmod(r[i] + x * a); r[i + 1] = pmod(r[i + 1] + x); }); g = r; } return g; }
  function rsParity(data, n = NSYM) { const g = rsGen(n), rem = new Array(n).fill(0).concat(data);
    for (let i = rem.length - 1; i >= n; i--) { const c = rem[i]; if (c) for (let j = 0; j < g.length; j++) rem[i - n + j] = pmod(rem[i - n + j] - c * g[j]); }
    return rem.slice(0, n).map(x => pmod(-x)); }
  function symbols(src) { const codes = [], toks = src.replace(/::/g, ": :").match(/#[0-9te]+|[!?~:]|[a-z]+/g) || [];
    for (const t of toks) { if (t[0] === "#") for (const c of t.slice(1)) codes.push(91 + DIGITS.indexOf(c));
      else if ("!?~:".includes(t)) codes.push(103 + "!?~:".indexOf(t));
      else { for (let j = 0; j < t.length - t.length % 2; j += 2) codes.push(CONS.indexOf(t[j]) * 7 + VOWELS.indexOf(t[j + 1])); if (t.length % 2) codes.push(84 + VOWELS.indexOf(t[t.length - 1])); }
      codes.push(109); } return codes; }
  const pword = v => v < 84 ? CONS[Math.floor(v / 7)] + VOWELS[v % 7] : CONS[Math.floor((v - 84) / 7)] + VOWELS[(v - 84) % 7] + "a";
  function eccTail(body) { const c = symbols(body), par = []; for (let k = 0; k < Math.max(1, c.length); k += BLOCK) par.push(...rsParity(c.slice(k, k + BLOCK)));
    return "=" + par.map(pword).join("-"); }
  const addEcc = src => src.split("|").map(v => v.trim()).filter(Boolean).map(v => v + " " + eccTail(v)).join(" | ");
  const api = {VM, parse, addEcc, eccTail, symbols, lex, ring, schedule, bindLoops, CANON, RATIO, VOWELS, CONS, DIGITS, isWord, fmt};
  if (typeof module !== "undefined") module.exports = api; else root.KANON = api;
})(this);
