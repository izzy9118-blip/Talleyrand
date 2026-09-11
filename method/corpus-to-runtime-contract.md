# Talleyrand Corpus-to-Runtime Contract

Record: TAL-CORPUS-RUNTIME-001

Version: 1.1.0

Status: IMPLEMENTATION_SPECIFICATION_PENDING_REVIEW

Runtime: NOT_OPERATIONAL

Authority boundary: owner agreement concerns the direction; this exact
implementation remains reviewable. No adapter or operational admission is created.

## Purpose and governing ground

The corpus establishes the particular intelligence under reconstruction. The
harness establishes the conditions under which an authorized minister investigates,
judges, and reports. Common transport must not impose another minister's intellectual
organization on Talleyrand.

This specification is subordinate to the Keel, the reflexive political-biography
protocol, and the quotation-grounded-abstraction protocol. It preserves their
passage-scale reading, prudence-centered reconstruction, and principles-before-deeds
sequence. It specifies documentary access and authority, not separate mental modules
or a fixed political decision formula.

Governing records:

- `keel.md`, especially principles 1, 8, 9, and 11.
- `memory_talleyrand/reflexive-political-biography.md`.
- `memory_talleyrand/quotation-grounded-abstraction.md`.
- `manifest.yaml`, `deeds/index.yaml`, and `ratification/live-owner-ratifications.yaml`.
- `speech/voice-license.yaml`.
- `ratification/2026-09-11-corpus-runtime-direction.yaml`.
- `studies/memoirs/corrections/2026-08-10-learning-and-principles-before-deeds.md`.

### Exact compatibility baseline

This revision continues the proposal at Talleyrand commit
`0323164678eea51c55a8d0e730a352bf073fadc4` in PR #36. The governing house
baseline is `aee9d9e676a6244f132357f89dae649e3fd1d42c` (manifest 1.31.0,
live deed corpus 2.12.0). The inspected Sanctum baseline is
`b26a16f4c94849c3a25d90239e907665086282b2`.
Exact paths, Git blob hashes, and the scope of this revision are recorded in
[`../governance/reviews/2026-09-11-corpus-runtime-contract-review.yaml`](../governance/reviews/2026-09-11-corpus-runtime-contract-review.yaml).
These are documentary baselines, not a certified Talleyrand minister pin.

At that Sanctum commit, `registry/ministers.yaml` establishes Strauss and
Xenophon and lists Talleyrand under `future_repositories`.
`registry/adapters.v1.yaml` binds each established minister's certified base
separately from its runtime overlay; `universal_dispatch.py` checks ancestry
and the exact changed-path set. The adopted overlays permit only
`sanctum_adapter.py`. A future corpus, loader, selection-policy, or
interpretation change therefore belongs in a separately reviewed minister base;
it cannot be smuggled into an overlay. Path conformance alone cannot establish
that transport code is intellectually neutral: that also requires review.

The external transport is `sanctum.adapter.v1`, using
`contracts/sanctum-adapter.schema.v1.json` (schema ID
`urn:sanctum:adapter:1.0.1`). This document specifies future obligations within
that interface. It neither supplies a conforming adapter nor asserts that the
current host already enforces the delivery requirements below. At integration,
compare the adopted pins and contracts with this baseline and record any change.

## 1. Preserve the existing reading as the primary reconstruction

The existing Memoirs units remain intact. Do not rewrite them mechanically, detach
their memorable sentences from their arguments, or cross-reference deeds prematurely.
Any access record is downstream of a specified unit and points back to its full
interpretation; it does not become a competing account of Talleyrand.

Keep the existing Build Harvest distinctions: Talleyrand-specific finding, prudence
candidate, and transferable abstraction. None may silently acquire the authority of
another. Where the text does not show an ordering of factors, record that limitation
instead of completing the argument from general knowledge.

A source's retrospective character is metadata to evaluate, not a reason to exclude
it. Distinguish a retrospective account of judgment from independent proof of what
the actor knew or intended at the time.

## 2. Register the witness before asserting source-level verification

Every supplied passage identifies its source, witness, language, attributed speaker,
edition, and printed locator. Preserve `[V]`, `[HT]`, editorial mediation, quotation
status, and unresolved transmission questions where applicable.

`TAL-SRC-010 / TAL-WIT-010` registers the English Volume I witness already identified
in the repository. Its unresolved scan identity, source hash, and digital page map
must remain unresolved until recovered. Registration is not acquisition or a new
quotation audit. A study-file hash proves which study was used; it does not prove
that the study matches an absent scan.

The French Vienna witness and its verified page pin do not verify English Memoirs
wording. A replacement scan or French alignment requires its own identified record;
never silently exchange witnesses.

## 3. Supply the complete relevant act of judgment

A future preparation record must identify the selected unit by repository commit,
path, and content hash, and distinguish that study identity from the underlying
source-witness identity. It must record why the unit was selected and the exact
authority in which each component is offered.

The reasoning context must actually contain the required passage text, not merely
a title, maxim, source identifier, path, or embedding match. Preserve a full paragraph
or contiguous sequence sufficient to show the object, causal or comparative movement,
qualification, and consequence. Cross printed page boundaries when the thought does.

Carry the associated local reading, factor distinctions, earned weighting, alternatives,
uncertainty, and applicable corrections with the passage. Their administrative labels
must not fragment a unified act of judgment. When necessary for understanding the
selection, supply the complete unit. An index locates the argument; it does not replace it.

Selection remains minister-local and visible. Record included and excluded material
with reasons, including relevant contrary passages and later qualifications. Do not
select only material that resembles a desired recommendation or treat search rank as
interpretive authority. Revisit the selection when new evidence changes the inquiry.

Record the bytes or exact text actually delivered and their hashes in the prepared
context record. If a required passage or qualification cannot fit, expand the context,
reduce the supported scope, or record a preparation failure. Do not silently truncate
it while claiming that its evidence was supplied.

### Minimum prepared-context contents

These operational preparation requirements apply only after the relevant house
authorization. During corpus formation, the independent Memoirs reading and
principles-before-deeds correction continue to govern selection; a future loader
must not become a filter on what the unread corpus is allowed to teach.

The future local builder must resolve the declared load order into actual
contents. Preserve the complete live deed set in index order, its applicable
owner-ratified sharpenings, and the governing records; relevance selection may
not silently prune or reorder that authorized base. Prose entries such as a
specified component of an amendment must resolve to an exact, bounded component,
not import the rest of a historical file as live authority. Record the Keel's
referenced reconstruction protocols, current source and voice limits, and
applicable corrections alongside that base. An unresolved required dependency
is a preparation failure, not a reason to use remembered instructions.

The following are documentary fields for auditing supplied material, not a
schema for dividing Talleyrand's thought into mental modules:

| Material | Required record and delivered content |
| --- | --- |
| Governing reconstruction | Manifest, Keel, declared live records and applicable amendments, exact authorization references, load order, and the complete texts that govern this preparation. |
| Selected episode | Stable unit reference; repository, commit, path and Git blob hash; full relevant contiguous passage windows with printed locators; associated local reading, qualifications, alternatives, and corrections. Supply the whole unit when separating these would distort the judgment. |
| Witness identity | Source/witness IDs, edition, language, attributed speaker and mediation; exact-copy identity and SHA-256 where established; verification scope, normalization, `[V]`/`[HT]` and unresolved copy binding. A study hash is a separate field. |
| Offered use and authority | Whether a component is source text, local reading, prudence candidate, transferable abstraction, or owner-adopted reconstruction; the purpose for which it is supplied; exact adoption reference or explicit lack of one. Preserve the repository's existing evidence marks independently. |
| Selection account | Inquiry and stage, selection procedure/version, material considered, inclusion and exclusion reasons, relevant contrary evidence and limits, and what was not searched or remains unresolved. Do not claim an exhaustive search merely because a selector returned results. |
| Derivation provenance | Producer identity, exact consumed records and commits, extraction or transformation version, predecessor context reference and reason for change. An editor's derivation is not attributed to Talleyrand. |
| External ground | Immutable common briefing and attributable Horus exchanges; separately pinned and explicitly selected Stars context where admitted. Preserve each source's jurisdiction and acquisition status in the supplied text. |

Material supplied as a candidate or as counterevidence may inform examination
within an authorized scope; it does not command a move. In particular, the
manifest's unresolved ore remains excluded from the live deed surface. Its
relevance as a research question or limit must be labeled without converting it
into a ratified capacity. Retrieval must not conceal a relevant contradiction
simply because it has not been adopted as doctrine.

### Preparation and actual delivery are separate records

An access record proves resolvability. A prepared context proves assembly. A
delivery receipt proves only the input actually submitted by the host. None
proves that the model understood or faithfully used the passage.

For each model call, the future host must preserve an auditable receipt with:

- inquiry ID, minister ID, Secretary stage/receipt reference and call ID;
- certified base and runtime overlay commits, manifest identity, contract
  version, prepared-context artifact and digest;
- the actual submitted input artifact and SHA-256, including the message or
  tool-result contents carrying each required passage, plus model/provider
  identity and the available submission/response evidence;
- a mapping from each required context item to its exact position in that
  input, with the supplied text's digest and length;
- the effective input budget, known truncation or transformation behavior,
  delivery failures, and exclusions with reasons;
- predecessor receipt/context references and reasons for any later reselection.

Hash raw artifact bytes with SHA-256; hash supplied text as its exact UTF-8
encoding, with every normalization recorded. Git blob hashes identify repository
objects and are not interchangeable with these digests. Store a digest outside
the artifact it hashes, avoiding self-referential hashes. Preserve the submitted
input or enough immutable inputs and serialization details to reconstruct it
byte for byte; a digest alone does not disclose the missing text.

Validate coverage against the final input after serialization and known host
transformations. On omission, unavailable required text, digest mismatch, or a
budget that cannot carry the required context, do not make that call with a
false delivery claim. Expand capacity where authorized, or explicitly narrow
scope and revalidate a new preparation. Missing evidence that only limits a
claim may remain a declared uncertainty; a missing required qualification may
not. Failed calls and unsent preparations retain their actual status. Unknown
provider-side behavior is an uncertainty, not proof of delivery or understanding.

At the inspected baseline, `federated_proving._prompt` serializes the inquiry,
prepared context, and prior Horus exchanges. `_journal_model_call` saves a
prompt hash and output metadata, but not the prompt text or an item-by-item
coverage receipt. Those functions alone do not satisfy this delivery contract.
Any necessary host implementation must be reviewed separately in Sanctum.

## 4. Keep study, interpretation, and authorization distinct

An existing study can remain available for research without becoming an instruction
that the minister must obey. An access record cannot promote a local observation into
a recurring capacity, a candidate into a ratified deed, or a generic abstraction into
Talleyrand's governing doctrine.

Future operational promotion requires review of the exact material and its scope,
the warranted evidence of recurrence or other explicit basis, applicable contrary
instances and limits, and a recorded owner decision. Apply that decision through the
house's declared manifest and index rather than an undocumented loader exception.
A correction record preserves the predecessor; changed text is not silently substituted.

Source registration, passage verification, interpretive adoption, house runtime
authorization, voice licensing, Sanctum admission, and report certification are
distinct acts. Approval of one does not imply any of the others. This specification
changes none of the existing activation or licensing states.

| Transition | Evidence and authority required |
| --- | --- |
| Passage to local reading | Exact witness-grounded text, local explanation and limits. Registration or a prior audit does not verify newly enlarged passages. |
| Local reading to reconstruction candidate | Explicit derivation, proposed scope, rival readings, contrary instances and the comparisons still needed. The candidate remains provisional. |
| Candidate to adopted reconstruction | Cross-case testing or another explicitly justified evidentiary basis; an owner decision bound to the exact text and scope; corresponding governing/index records. Adoption of a method does not adopt every conclusion produced under it. |
| Adopted reconstruction to operational use | An explicit house authorization identifying the exact reconstruction, interface, scope and limits, followed by owner-authorized Sanctum admission and certified base/overlay bindings. Existing deed ratification alone is insufficient. |
| Operational output to certification | The report's provenance, uncertainty and dissent, structural validation and independent review, then the applicable owner certification act. A successful call or test cannot supply that act. |

Apply the already granted authority to its exact scope; these distinctions do
not require reapproval of unchanged owner-ratified material. Preserve predecessor
commits and adoption/correction records. A revision to an adopted text, loader or
selection policy must not inherit authority merely by retaining a filename.
Semantic completion and final teaching remain separate from any future bounded
operational authorization. Voice imitation requires its own scoped license;
the absence of a general voice license is not itself a demand to imitate voice
before authorizing a bounded, candid ministerial report.

## 5. Support inquiry, not a predetermined answer

A selected episode may support proposed information needs only to the extent its
reading warrants them. Mark our modern transfer questions as derived proposals,
not quotations or newly discovered historical statements.

A future authorized minister must be able to state what he needs to learn, which
source requirements would answer it, what evidence could defeat or qualify his
provisional judgment, and which parts of that judgment change after the evidence
arrives. Those requests pass through Sanctum's investigative and adversarial Horus
processes. Do not create a parallel, privately curated evidence channel.

Keep current-case evidence acquired through Horus distinct from minister-corpus
ground and explicitly selected Stars research. Historical analogy is not proof of
a present event. Do not treat unsearched or unacquired material as evidence of absence.

Prudence has no fixed numeric weighting or universal ordering of selected factors.
A recommendation must answer to the actual situation and the ends the corpus
supports, including grounds for action, withdrawal, revision, or nonaction.
Unknowns remain visible; they do not automatically require either paralysis or
unwarranted certainty.

Each derived information need must identify the passage or adopted reconstruction
that motivates it, the proposition it could change, and the sources capable of
discriminating among the live alternatives. Express actors, dates, language and
source requirements through the adopted Horus contracts. Historical passages may
motivate the questions; evidence acquired for the present inquiry must answer them.

## 6. Preserve sovereignty, candor, and the unified report

The future house adapter may expose Sanctum's common `describe`,
`validate-interface`, `prepare-request`, and `validate-report` operations while
retaining local context assembly and validation. Follow the adopted transport
contract at the actual integration step; do not invent a new universal protocol.

Keep the approved corpus pin separate from transport changes. No change here
repins an established minister, edits another repository, or activates a model call.
Until separately authorized, the house remains `FOUNDING` and `NOT_OPERATIONAL`.

Talleyrand speaks candidly within Sanctum. Understanding reserve, audience,
indirection, or concealment in historical or contemporary actors is analytical
equipment, not permission to withhold his grounds or material uncertainty from the
Assembly. An earned verdict remains joined to its evidence and accountable explanation;
a personality costume or an unexplained oracle is not the minister.

Do not rewrite the historical reconstruction to force agreement with the Assembly's
foundation or let one historical minister silently determine the Assembly's ends.
Preserve attributable agreement and disagreement through the common report process.

### Mapping to the adopted interface

| Operation | Future Talleyrand responsibility |
| --- | --- |
| `describe` | Identify the minister, repository, exact runtime checkout, manifest and protocol; disclose scope and the current authority state. Do not describe a prospective binding as adopted. |
| `validate-interface` | Validate the external contract and local dependency/authority bindings. Report structural conformance only; no model call, admission or semantic certification follows from this operation. |
| `prepare-request` | Preserve inquiry identity, question, immutable briefing and requested repository pin; assemble the full local context and its auditable selection record. Keep the certified base distinct from the runtime overlay. |
| `validate-report` | Validate the bounded sovereign report against its adopted local/common contracts and source/authority limits, retaining proposition provenance, uncertainty, dissent and termination status. Do not raise an interpretation's evidence kind through rhetoric or return an owner certification. |

Under the inspected dispatcher, request `repository_pin.commit` and prepared
`repository_commit` identify the runtime overlay; the dispatcher adds
`certified_base_commit` separately. Do not replace the overlay value with the
base in the common fields. The prepared request's `context` object can carry
the minister-local contents and access metadata without changing the universal
schema. Required host delivery receipts are additional integration work, not
existing common fields or a new claim of Sanctum authority.

### Evidence across the investigative stages

All calls remain within authorized Sanctum rounds and Secretary sequencing.
Use these stage dependencies when implementing and testing delivery:

| Stage | Required relationship to earlier material |
| --- | --- |
| Investigative request | Full applicable governing/episode context and immutable inquiry; derived information needs and source requirements tied to the judgment they could change. Horus retains its ordinary source-selection independence. |
| Provisional judgment | The same accountable context, the investigative request and its actual acquisition result, including unfilled needs; provisional propositions and the evidence that could weaken them. |
| Adversarial evidence request | The exact provisional propositions and their disconfirming needs, bound to the investigative query through the adopted Horus process. A mechanical stage is not falsely recorded as a separate model call. |
| Final judgment | The exact provisional judgment plus investigative and adversarial requests/results; an account of retained, revised, withdrawn or unresolved propositions and the reasons. Newly warranted propositions identify their new ground. Retaining a judgment may be warranted; change is not a test score in itself. |
| Native report and genealogy finalization | The exact final package and evidence bindings; the native report must preserve its substantive propositions and limits rather than generate an unbound second judgment. |

The current `_prompt` receives prepared context and Horus exchanges; those
exchanges do not by themselves deliver the provisional judgment or final package.
Explicit delivery and consistency of those products are therefore future
integration requirements, not achievements claimed for the existing code.
When new evidence warrants further corpus retrieval, record an attributable
local context revision, carry relevant counterexamples forward, and leave the
common briefing unchanged. If the host cannot accept that revision lawfully,
record the limitation or require a new authorized preparation rather than
silently adding facts or replacing a frozen context.

## 7. Acceptance requirements for later implementation

These are requirements, not assertions that the corresponding code or tests already
exist. A documentary preparation check is not a ministerial run.

| Check | Required result |
| --- | --- |
| Source resolution | Distinguish the registered edition, exact acquired copy, study record, and supplied excerpt; unresolved fields stay explicit. |
| Passage delivery | Show that the selected text and necessary qualifications were included in the actual prepared context. A path alone fails. |
| Submitted-input coverage | Removing a required passage after preparation, truncating its qualification, substituting a digest, or changing its bytes must fail delivery validation. A prepared-context check alone is insufficient. |
| Scope and authority | Reject automatic candidate promotion or an attempt to use this preparation as runtime admission. |
| Base and overlay | Reject a pin mismatch or a forbidden changed path; separately review whether transport or selection code changes the material governing judgment. |
| Speaker and language | Preserve translated wording, retrospective testimony, editorial voices, and source-specific verification limits. |
| Selection integrity | Explain the chosen windows and exclusions; retain relevant counterevidence and corrections. |
| Correction history | Preserve the exact predecessor and explain what changed and why. |
| Stage continuity | Fail a final-stage input that omits the provisional propositions; fail a native report that changes the final package's substantive claims without an attributable revision. |
| Behavioral fidelity | After separate run authorization, test whether materially changed circumstances alter the judgment where the reconstructed reasoning requires it. |
| Certification boundary | Structural tests establish their stated mechanical results only; substantive fidelity remains open to owner probing. |

Unit 21 is the proposed first access-record example. Its full argument must remain
available; a title such as "yield before compulsion" is insufficient. A later contrast
test may change the evidence about whether resistance remains viable and examine
whether the recommendation responds. That is a proposed transfer test, not a historical
finding, a completed evaluation, or authorization to run Talleyrand now.

For that later test, vary the evidence about the viability of resistance, the
influence actually retained by concession, and the costs to the larger good.
Hold wording-only changes apart from material changes. Test both a case where
the lost position and preservable remainder are evidenced and a case where
they are not; include contrary ground and allow warranted uncertainty. Assess
whether the questions and judgment follow those differences, not whether an
expected slogan appears. Unit 21's retrospective assessment of inevitability
remains contestable; the test is a modern transfer proposal, not a historical
counterfactual certified by the Memoirs.
