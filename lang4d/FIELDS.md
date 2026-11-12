# KANON for a field: physics, machine learning, spacecraft guidance, AI satellites (round 68)

## 1. The honest starting point

Fields do not adopt languages for novelty. They adopt them for four things, in this order:
1. **An ecosystem.** Libraries, people and decades of code.
2. **Performance** on their hardware.
3. **Certification and trust.** In flight software this means process standards such as DO-178C, NASA NPR 7150.2 and ECSS-E-ST-40C, and coding rules such as MISRA C or SPARK Ada.
4. **One capability nobody else has.**

KANON cannot win the first three anywhere:

| Field | What runs the field today | Can KANON replace it? |
|---|---|---|
| Physics computing | Python (NumPy, SciPy), Julia, Fortran, C++ on clusters and GPUs | No. KANON is an interpreter of number lists. |
| Machine learning | Python with PyTorch or JAX, kernels in CUDA or Triton | No. KANON has no tensors or GPUs, and should not try. |
| Spacecraft guidance, navigation and control | C and C++ (NASA cFS, JPL F Prime), Ada/SPARK, Rust emerging; models in MATLAB/Simulink | No. Guidance algorithms need certified, hard-real-time native code. |
| Satellite operations | Procedure languages: ECSS PLUTO (ECSS-E-ST-70-32C), SCL, STOL, NASA PLEXIL; CCSDS telecommand and telemetry | **Partly, and this is the opening.** |

So the strategy is **not** "rewrite physics, ML or guidance in KANON". It is to become the standard for one layer that every one of these fields is growing and that nobody owns:

> **The verifiable command layer: the short programs that humans and autonomous machines hand each other. A person must be able to hear them, check them and trust them, and a machine must be able to prove their bounds.**

Autonomy makes this layer bigger every year. AI agents propose actions, satellites plan on board, labs run robotic experiments, and in each case someone must approve a short program they did not write. That is where a disruptive entrant wins. The incumbents serve this layer poorly:
- **Natural language** cannot be verified.
- **Raw code** cannot be read aloud.
- **Procedure languages** are typed-only and assume a screen.

## 2. What KANON uniquely combines

No incumbent offers all seven:

| Property | Status | Evidence |
|---|---|---|
| **Heard and spoken** exactly: the program is its own audio | Built | Studio channel exact at 4 dB SNR. Phone channel exact through phone band, GSM and G.726 (40 of 40). |
| **Repairs itself and never fails silently** | Built | Reed–Solomon over GF(113): 2 symbols repaired per block, 3–4 always flagged. No silent errors in any test. |
| **Seen at a glance**: the seal fingerprint and execution order | Built | Equal programs draw equal seals; the ring arcs show execution order. |
| **Statically bounded**: proven step and memory limits before running | Built (KANON-FLIGHT profile) | The compliant procedure passes with 9 steps and 1 value; the violating one fails rules F1–F6. |
| **Unit-safe**: physical dimensions as words you can hear | Built (`units.py`) | 7 SI base units ↔ 7 vowels. Dimension errors are refused; speed is spoken *pani*, force *popanini*. |
| **Small and closed**: 19 glyphs and 84 syllables, learnable in a course | Built, not yet measured | 30-step course; a learner study is pending |
| **Culture- and language-neutral**: no English keywords | Built | Syllables, not words |

## 3. The design: one core, four field profiles, bridges out

```
                    ┌───────────────────────────────────────────────┐
  people ◀──────▶   │  KANON CORE  text · speech · seal · ECC · VM  │   ◀──────▶  machines
  (ear, eye,        └──────┬──────────┬──────────┬──────────┬───────┘     (cFS / F Prime,
   voice)                  │          │          │          │              PyTorch, ROS 2,
                   KANON-FLIGHT  KANON-AGENT  KANON-LAB   KANON-ML         EPICS, agents)
                   procedures,   AI action    units,      experiment
                   telecommand   approval     protocols   specs, evals
                           │          │          │          │
                    bridges: transpile to C command tables / Python / JAX · CCSDS packets ·
                    PLUTO import and export · ROS 2 actions · MCP tool for LLM agents
```

A **profile** is the core language plus:
- a restricted rule set, checked statically;
- a domain Canon house;
- a bridge.

The core never changes per field. That keeps one course, one codec and one seal across all of them.

### 3.1 KANON-FLIGHT: spacecraft and satellite operations (the beachhead)

**The problem.** Operations teams write procedures (pass plans, burns, safing, payload sequences). The procedures are reviewed on screens, read aloud on voice loops ("go/no-go", readback), and uplinked as telecommands. Readback errors and procedure errors are a known class of operational incident. Readback is plain voice with no check.

**What the profile gives:**

| Need | KANON-FLIGHT | Status |
|---|---|---|
| No runaway execution | F1 every loop bounded; F2 no recursion; F4 memory bound; a worst-case step count | **Built:** `fields/profile.py` |
| No unapproved code | F3 only approved library words | **Built** |
| No command without a check | F5 every command word guarded (`?`) | **Built** |
| Link protection | F6 every verse carries Reed–Solomon. This mirrors CCSDS practice, where telemetry already uses RS(255,223). | **Built** |
| **Machine-checked readback** | The controller speaks the verse on the voice loop. The ground system decodes the voice loop and compares the seal with the approved procedure, so a misspoken step is caught before uplink. | **Channel built** (phone mode survives GSM and G.726). Integration is next. |
| Flight execution | Transpile to a C command table for cFS or F Prime, so the on-board side runs certified native code, not the KANON VM | Next |
| Standards interop | Import and export ECSS PLUTO procedures | Next |
| Units on every parameter | Burn Δv in *pani* (m/s), thrust in *popanini* (N), checked at the interface | **Built:** `fields/units.py` |

**First adopters:**
- university CubeSat teams, who write their own operations software and are open to new tools;
- amateur-radio satellite operators, who command over voice-grade radio;
- analog-astronaut and mission-simulation programmes.

They can adopt without certification. Their results become the evidence base.

### 3.2 KANON-AGENT: autonomous AI, including AI satellites

**The problem.** An AI system on a satellite, or an agent on a computer, proposes an action plan. The ground team or user must approve exactly that plan. Bandwidth is small, latency is long, and approval is often by voice or a short message.

**The design:**
1. **The agent emits its plan as a KANON-FLIGHT verse, never as free text.** It is statically bounded and guarded, with units.
2. **Approval is by seal and ECC.** The human hears the verse, or sees its seal. Approval returns the verse's checksum.
3. **The executor runs only a plan whose checksum matches the approval.** The executor runs on board for a satellite, or locally for a software agent. "What was approved is what runs" becomes a property of the channel, not a hope.
4. **Downlink is compact.** A plan of 20 words is a few hundred bits, plus parity, which is cheap even on a low-rate link.
5. **For language-model agents:** expose `propose_kanon(plan)` and `approve(seal)` as tools, for example through the Model Context Protocol. The model can use any language internally; only KANON crosses the trust boundary.

This is the strongest disruptive case. Every lab building agentic AI needs a human-checkable action format, and none has emerged.

### 3.3 KANON-LAB: experimental physics and lab automation

**The problem.** Experiments are run by people with busy hands (cleanrooms, beamlines, gloveboxes) and increasingly by robots. Unit mistakes and undocumented protocol changes damage reproducibility.

**The design:**
- **Units.** Every quantity carries its dimension; the 7 SI base units map to the 7 vowels (`units.py`, built).
- **Spoken protocols.** A protocol is a verse. Its seal is the protocol's identity, written into the data file, so the data always records exactly which protocol produced it.
- **Hands-free entry** in the phone channel, which works through ordinary headsets and radios.
- **Bridges** to the Python-based control systems large facilities already use (EPICS, Bluesky, ROS 2), so KANON issues commands and the existing stack executes them.
- **A statistics house** built from this project's own methods: permutation tests, exact p-values and multiple-testing correction. Analysis plans can be pre-registered as sealed verses.

### 3.4 KANON-ML: machine-learning experiments, evaluations and governance

KANON does not train models. It **specifies** and **governs** them:
- **Experiment and evaluation specifications** as sealed verses: the dataset seal, hyper-parameters with units (learning rate dimensionless *ki*, budget in seconds *pi*), and the metrics to report. The seal travels into the model card, so it is clear which specification produced which model.
- **Pre-registered evaluations.** The evaluation verse is sealed before the run, so it cannot be changed after seeing results. This is the same discipline as this project's pre-registered rounds.
- **Agent action approval**, as in 3.2.
- **Bridges** to Python, PyTorch and JAX configuration, so KANON specifies and Python executes.

## 4. Why this could be disruptive

Disruptive innovations enter where incumbents overserve or do not serve, with something simpler that improves until it moves up-market. Here:
1. **Entry.** CubeSat operations, hobby radio satellites, lab hands-free control and agent approval demos. These are users no incumbent tool serves well, and certification is not demanded.
2. **The improvement path:**
   - a measured readback-error reduction;
   - a learner study that confirms fast learning;
   - flight-heritage on small satellites;
   - transpilation to certified C, so the verified native code is what flies and KANON stays the human interface.
3. **Moving up-market.**
   - **Space:** an ECSS/CCSDS-aligned procedure profile, proposed as an annex to the procedure-language standards.
   - **AI:** a "speakable plan format" for agent approval, proposed to agent-framework maintainers.

## 5. Evidence still needed

Each item below is a claim the plan depends on, with the experiment that would settle it.

| Claim | Experiment | Done |
|---|---|---|
| Survives real voice channels | Phone band, GSM, G.726, Opus (`fields/channels.py`) | **Yes, with limits:** phone mode exact on phone, GSM and G.726. Opus at 16 kbit/s gets 35 of 40 and 8 kbit/s 16 of 40, all failures flagged. |
| Survives real radios | Software-defined radio, narrowband FM and SSB, over the air | No |
| Machine readback beats plain readback | Simulated voice-loop operations: error rate with KANON readback against plain language, on the same procedures | No |
| Learnable fast | The one-night course, timed, with next-morning retention | No |
| Humans can speak it to the decoder | Human-voice front end (formant vowels plus a consonant classifier) | No |
| Flight execution is safe | Transpile to C, run on cFS or F Prime in simulation, compare against the VM on every program | No |
| The agent approval loop works | An LLM agent emits KANON plans; users approve by ear; measure wrong-approval rate | No |

## 6. Build order

1. **The KANON-AGENT demonstration.** Agent → verse → spoken plus seal → approval → checksum-gated execution. It is the most visible and the least regulated.
2. **The C transpiler** for KANON-FLIGHT, and a cFS or F Prime command-table bridge, run in simulation.
3. **Field trials of machine-checked readback** on a voice loop with a CubeSat team.
4. **Over-the-air radio tests** with a software-defined radio.
5. **The learner study.**
6. **Standards outreach:** a PLUTO bridge and a CCSDS-aligned profile document.

## 7. Built in round 68

- **`fields/units.py`**: physical dimensions as chords of the seven planes. Results: `fields/units_results.txt`.
  - Checks passed: the rocket equation (9,349 m/s), a 400 km orbit (7,673 m/s), kinetic energy, photon energy.
  - Refused: mass + time, the log of a dimensioned mass, thrust compared with energy.
  - The Mars Climate Orbiter case is a *scale* error (lbf·s against N·s, the same dimension, *popani*). A dimension check alone cannot catch it, and the file says so. Declaring units at the interface converts it automatically.
- **`fields/profile.py`**: the KANON-FLIGHT static checker (rules F1–F6, worst-case steps, memory bound, seal). Examples: `fields/burn_ok.kn` passes; `fields/burn_bad.kn` fails all six rules.
- **The phone channel profile in `kanon.py`.** Every tone sits inside 300–3400 Hz, vowels are pure tones, and a burst counts only if it beats the vowel band.
  - **Correction to earlier claims.** The original (studio) codec scored **0 of 40** on a telephone line. Earlier statements that it is "DTMF-grade" or carried by "any phone line" were wrong for the studio channel.
  - The phone channel scores 40 of 40 through a phone line, plus noise, GSM and G.726.
  - `fields/channels.py` gives the full table.
