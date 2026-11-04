# Adaptivity boundary — Mealy machines (extraction textuelle)

> Extraction textuelle du document DOCX source `Adaptivity boundary - Mealy machines.docx`, Library path `/Recherche/02_PROGRAMMES_ACTIFS/Observabilite/Notes/Adaptivity boundary - Mealy machines.docx`.
>
> Ce fichier Markdown est une représentation textuelle pour consultation. Il ne remplace pas le fichier DOCX original et ne préserve pas sa mise en page, ses tableaux ni ses objets incorporés.
























Compatibility Nerves and Conflict Spectra in Adaptive State Identification

Compatibility nerves and conflict spectra in Mealy state identification
Compatibility Nerves and Conflict Spectra
in Adaptive State Identification
Sharp bounds for 1-step exact trace languages of deterministic Mealy machines
Research note — revised 27 September 2026
Abstract
We study when adaptive state identification in a complete deterministic Mealy machine can or cannot be compiled into a preset experiment under the locality assumption r_IO = 1: a finite input-output trace is realizable exactly when all of its consecutive length-2 factors are realizable. Two structures emerge. First, the number of output branches that can remain genuinely fertile after one input is at most |Γ|−1; this bound follows from uniform finite-valuedness of the local trace transducer and is sharp. Second, for a knowledge state K, each output branch has a regular language of preset continuations that resolve it. The nerve of these resolution languages records which branches admit a common preset continuation. If an ADS exists but no PDS exists, some reachable node contains a minimal empty-intersection subfamily—a conflict core. Under r_IO = 1 every conflict core has arity between 2 and |Γ|−1. Conversely, every arity k in {2,…,|Γ|−1} is realizable by an explicit family with r_IO = 1, ADS depth 2, and no PDS. The binary-output collapse L_P = L_A becomes the degenerate case in which no conflict core can exist. We retain a separately audited minimal ternary witness with (|Q|,|Σ|,|Γ|)=(5,2,3). The ingredients from ADS/PDS theory and bounded ambiguity are classical; the compatibility-nerve formulation and conflict-spectrum theorems have not been located in the literature searched so far and remain candidate results pending external review.
1. Main results
A preset distinguishing sequence (PDS) uses one fixed input word for all possible initial states. An adaptive distinguishing sequence (ADS) is a decision tree in which the next input may depend on the outputs already observed. ADSs are strictly more powerful in general, and the algorithmic gap between ADS and PDS is classical [1]. The present note asks what survives of that advantage when the observable trace language is exactly 1-step local.
Theorem 1 (fertile-width bound). Let M be a complete deterministic Mealy machine with q=|Γ| outputs and r_IO=1. For any input a, at most q−1 output symbols (a,y) can be fertile, meaning that some common future input word admits at least two distinct future output continuations. Hence the global fertile width w(M) satisfies w(M)≤q−1.
Corollary 2 (binary collapse). If |Γ|=2, r_IO=1, and M admits an ADS, then every successful ADS is a comb and can be compiled into a PDS of exactly the same worst-case depth. Thus L_P=L_A.
Theorem 3 (conflict-core bound). Suppose a reachable knowledge state K admits an ADS but no PDS. Then some reachable ADS node has individually PDS-resolvable output branches whose resolution languages have a minimal empty-intersection subfamily C. Under r_IO=1 its arity satisfies 2≤|C|≤|Γ|−1.
Theorem 4 (sharp conflict spectrum). For every q≥3 and every k with 2≤k≤q−1, there exists a complete deterministic Mealy machine C(q,k) with r_IO=1, an ADS of depth 2, no PDS, and a root compatibility nerve whose unique minimal missing face has size k. Thus every conflict arity allowed by Theorem 3 is realizable.
The earlier binary/ternary boundary is therefore a corollary of a more general picture: binary outputs forbid conflict cores altogether; three outputs allow pairwise conflict; four outputs are the first case in which a genuinely ternary conflict can occur even though every pair of branches has a common preset resolver.
2. Definitions
A complete deterministic Mealy machine is M=(Q,Σ,Γ,δ,λ), with transition δ:Q×Σ→Q and output λ:Q×Σ→Γ. All q∈Q are possible initial states. A finite input word a₁…aₙ produces from q a unique output word y₁…yₙ and hence a trace ((a₁,y₁),…,(aₙ,yₙ)). Let L(M) be the set of all finite traces over all initial states.
We write r_IO=1 when a nonempty trace word belongs to L(M) exactly when every symbol occurs in L(M) and every adjacent pair occurs in L(M). Equivalently, the observable language equals its 1-step local closure.
For state identification it is useful to preserve initial identity. A knowledge state is a finite set K⊆Q_initial×Q_current. Initially K₀={(q,q):q∈Q}. After input a and observed output y,
K(a,y) = {(q₀, δ(q,a)) : (q₀,q)∈K and λ(q,a)=y}.
A preset word u resolves K if distinct initial identities represented in K produce distinct output words under u from their current states. Let R(K)⊆Σ* be the language of all such resolving words. A singleton knowledge state has R(K)=Σ*. If two initial identities have already merged into the same current state, then R(K)=∅.
An ADS is a finite rooted tree whose internal nodes are inputs and whose outgoing edges are output symbols; each leaf identifies one initial state. L_A is the optimal worst-case depth. A PDS is a single word u∈R(K₀); L_P is the shortest length, or ∞ if R(K₀)=∅.
3. Fertile output symbols and bounded ambiguity
Fix an input a. An occurring symbol (a,y) is called fertile if there exists a future input word u for which two distinct future output words are possible after a trace ending in (a,y). Let w(a) be the number of fertile outputs for input a and w(M)=max_a w(a).
Under r_IO=1, the local trace graph is exact: every path permitted by adjacent observable symbols is a genuine trace. For a fixed input a, and for every future input word u ending again in a, define a nonnegative integer matrix M(u) indexed by the occurring outputs of a. The entry (i,j) counts distinct local trace paths starting after (a,i) and ending after (a,j) under u. Concatenation of continuation words is matrix multiplication. Completeness gives every row sum at least 1, while determinism with finitely many initial states gives a uniform upper bound on every row sum. This is the finite-valued / bounded-ambiguity mechanism familiar from classical automata theory [2,3].
Lemma 5. If all q outputs of input a occur, they cannot all be fertile.
Proof. For output i let h(i) be the maximum possible row sum of row i among all return matrices M(u). The maximum exists because row sums are positive integers uniformly bounded by |Q|. If every output were fertile, every h(i) would be at least 2. Choose i with h(i)=m minimal and choose a matrix A with row-sum_i(A)=m. Select j with A(i,j)>0. Since h(j)≥m, choose a matrix B with row-sum_j(B)≥m. Every row sum of B is at least 1. Therefore
row-sum_i(AB) ≥ A(i,j)·m + (m−A(i,j)) = m + A(i,j)(m−1) > m,
contradicting the definition of h(i). If fewer than q outputs occur after a, the conclusion w(a)≤q−1 is immediate. Hence w(a)≤q−1 for every input a. ∎
4. Resolution languages and the compatibility nerve
Proposition 6 (resolution identity). For every knowledge state K and input a,
R(K) ∩ aΣ* = a · ⋂_{y : K(a,y)≠∅} R(K(a,y)).
Proof. Different first outputs already separate different branches. Therefore a word av resolves K exactly when its suffix v resolves every nonempty branch K(a,y) simultaneously. ∎
This identity isolates the source of irreducible adaptivity. An ADS may choose a different continuation in each branch; a PDS requires one continuation belonging to all branch-resolution languages at once.
For fixed K and a, define the compatibility nerve N(a,K) on the nonempty output branches by
S ∈ N(a,K)  ⇔  ⋂_{y∈S} R(K(a,y)) ≠ ∅.
This is a simplicial complex: every subset of a compatible family is compatible. A conflict core is a minimal nonface C: the full intersection over C is empty, while every proper subfamily has a nonempty intersection. Its cardinality is the conflict arity.
Each language R(K) is regular. One finite recognizer tracks, for every pair of initial identities still not separated, the corresponding pair of current states; a pair is deleted as soon as its outputs differ. Hence compatibility intersections and conflict cores are decidable by finite-state search.
5. Conflict cores are necessary and sharply bounded
Theorem 7 (necessary conflict core). If a reachable knowledge state K has an ADS but no PDS, then some reachable node of a successful ADS has a conflict core.
Proof. Choose a deepest node K′ in a successful finite ADS such that R(K′)=∅. Every nonempty child K′(a,y) then has a PDS, otherwise a deeper no-PDS node would exist. Thus every branch language R(K′(a,y)) is nonempty. Their full intersection is empty by Proposition 6, because otherwise a followed by a common resolver would be a PDS for K′. A finite family with empty intersection has a minimal empty-intersection subfamily. ∎
Corollary 8 (conflict-core bound under r_IO=1). If r_IO=1 and q=|Γ|, every conflict core arising as above has arity 2≤k≤q−1.
A singleton branch cannot belong to a minimal conflict core because its resolution language is Σ*. Hence every core branch contains at least two still-distinguishable initial identities and is therefore fertile. Theorem 1 gives k≤w(a)≤q−1. The lower bound k≥2 follows because each individual branch has a nonempty resolution language.
For q=2 the interval 2≤k≤1 is empty. Thus ADS-without-PDS is impossible under r_IO=1. Moreover w(M)≤1 forces every successful ADS to be a comb, recovering the stronger equality L_P=L_A.
6. Every allowed conflict arity is realizable
Fix q≥3 and 2≤k≤q−1. Define C(q,k) with states
Q = {x(i,0), x(i,1) : 0≤i<k} ∪ {s},
inputs Σ={a,t₀,…,t_{k−1}}, and outputs Γ={0,…,q−1}. Unused output symbols are allowed when q>k+1. The transitions are:
Input a: each x(i,b) self-loops with output i; s self-loops with output k.
Input t(j) on pair i=j: both x(j,0) and x(j,1) output 0 and move to s (the pair is destroyed).
Input t(j) on pair i≠j: x(i,b) outputs b∈{0,1} and moves to s (the pair is distinguished).
From s, every input outputs k and stays in s.
Proposition 9. For C(q,k), r_IO=1, L_A=2, L_P=∞, and the k branches created by input a form one conflict core of arity exactly k; every proper subfamily is compatible.
Proof. After the first a, output i<k leaves the pair {x(i,0),x(i,1)}, while output k identifies s. In branch i, any t(j) with j≠i distinguishes the pair, so an ADS resolves the machine in depth 2. A preset word containing only a never distinguishes any pair. At the first t(j), branch j is merged irreversibly into s, so no PDS exists.
For the nerve, any proper subset S of the k pair branches omits some index j; the one-letter continuation t(j) resolves every branch in S. For the full set of k branches, the first non-a input must be some t(j), which destroys branch j, so no common resolver exists. Thus the full k-set is the unique minimal missing face.
Finally, r_IO=1 is immediate from the exact current-state sets determined by the last observable symbol: after (a,i) with i<k the current set is exactly the pair {x(i,0),x(i,1)}; after (a,k) or any occurring symbol with input t(j), the current state is exactly s. Hence every locally admissible path remains globally realizable. ∎
This construction proves that every arity in {2,…,q−1} occurs. No state- or input-minimality is claimed for C(q,k) in general.
7. Pairwise compatibility is not enough
The first genuinely higher-order phenomenon occurs at q=4, k=3. The three branches A,B,C satisfy pairwise compatibility: there is a preset continuation resolving A and B together, another resolving A and C, and another resolving B and C. Nevertheless no single continuation resolves all three.
R(A)∩R(B) ≠ ∅,   R(A)∩R(C) ≠ ∅,   R(B)∩R(C) ≠ ∅,   but   R(A)∩R(B)∩R(C) = ∅.
Therefore a graph of pairwise conflicts cannot characterize irreducible adaptivity. The full compatibility nerve is required. In particular, conflict structure is genuinely higher-order once |Γ|≥4.
8. Minimal ternary witness with two inputs
The spectrum construction above is not input-minimal. Separately, the following five-state, two-input, three-output machine has been audited as a componentwise minimal witness to r_IO=1, finite ADS, and no PDS.
	state
	a
	b

	P₀
	0 → Q₀
	0 → S

	P₁
	0 → Q₁
	1 → S

	Q₀
	1 → P₀
	2 → S

	Q₁
	1 → P₁
	2 → S

	S
	2 → S
	2 → S


For this machine r_IO=1, L_A=3, and L_P=∞. The ADS first applies a; output 2 identifies S, output 1 leaves P₀/P₁ and b separates them, while output 0 leaves Q₀/Q₁ and requires a then b. Any first occurrence of b in a preset word separates one phase-pair but merges the other phase-pair into S. A separate proof shows that no machine with at most four states can realize ADS-without-PDS under r_IO=1; one input gives no genuine adaptivity and two outputs are excluded by Corollary 2. Hence (5,2,3) is componentwise minimal for this specific phenomenon.
9. Computational certificates
Two independent standard-library Python certificates accompany this note. The first checks the minimal (5,2,3) witness by three finite searches: exact 1-step language closure, Bellman ADS depth, and closure of the preset-configuration graph. It certifies r_IO=1, L_A=3, and L_P=∞.
The second certificate constructs C(q,k) and checks representative conflict cores. Exact runs for (q,k)=(3,2),(4,2),(4,3),(5,2),(5,3),(5,4),(6,5) all return r_IO=1, L_A=2, L_P=∞ and the expected unique minimal missing face of arity k. These computations corroborate the general proofs; they are not used as substitutes for them.
10. Relation to prior work and novelty status
ADS/PDS state identification is classical. Lee and Yannakakis established the basic separation and complexity gap [1], while modern work on splitting trees and minimum-cost ADS construction develops adaptive separating structures in detail [4,5].
The bounded-ambiguity and finite-valuedness mechanisms used in Theorem 1 are also classical. Weber and Seidl characterize finite versus infinite ambiguity in finite automata [2], and Weber studies finite-valued transducers and their decomposition [3]. This note does not claim a new ambiguity theorem.
The candidate contribution is instead the bridge from exact 1-step input-output trace languages to (i) the sharp fertile-width bound w≤|Γ|−1, (ii) the compatibility nerve of branch-resolution languages, (iii) the conflict-core bound 2≤k≤|Γ|−1 for ADS-without-PDS, and (iv) realization of every permitted arity. Targeted searches conducted for this revision did not locate this exact formulation or these bounds under ADS/PDS, splitting-tree, bounded-ambiguity, finite-valued-transducer, or sofic/1-step terminology. This is negative evidence only. Novelty remains unverified until expert external review.
11. Discussion and next questions
The results separate two notions that were previously conflated. Fertile width counts how many branches can remain potentially informative, but width alone does not determine whether adaptivity is irreducible: several fertile branches may still share one common preset resolver. The compatibility nerve records the higher-order obstruction that actually matters.
The most natural next questions are therefore structural rather than numerical: characterize the possible compatibility nerves under r_IO=1; determine whether additional automata-theoretic restrictions imply Helly-type bounds smaller than |Γ|−1; and identify classes for which every compatibility nerve is a simplex, equivalently every locally resolvable set of branches admits a common preset continuation.
A second direction is algorithmic. Since each resolution language R(K) is regular, one can compute compatibility and conflict cores by automata intersection, but the optimal complexity and the relation to classical PDS complexity remain to be determined.
References
[1] D. Lee and M. Yannakakis, “Testing Finite-State Machines: State Identification and Verification,” IEEE Transactions on Computers 43(3), 306–320, 1994. doi:10.1109/12.272431.
[2] A. Weber and H. Seidl, “On the Degree of Ambiguity of Finite Automata,” Theoretical Computer Science 88(2), 325–349, 1991. doi:10.1016/0304-3975(91)90381-B.
[3] A. Weber, “Decomposing Finite-Valued Transducers and Deciding Their Equivalence,” SIAM Journal on Computing 22(1), 175–202, 1993. doi:10.1137/0222014.
[4] M. Soucha and K. Bogdanov, “State Identification Sequences from the Splitting Tree,” Information and Software Technology 123, 106297, 2020. doi:10.1016/j.infsof.2020.106297.
[5] S. Güniçen, K. İnan, U.C. Türker, and H. Yenigün, “Effective Algorithms for Constructing Minimum Cost Adaptive Distinguishing Sequences,” Information and Software Technology 74, 69–85, 2016. doi:10.1016/j.infsof.2016.02.001.
Supplementary files: mealy_boundary_certificate.py; conflict_nerve_certificate.py. This draft deliberately avoids novelty claims stronger than the evidence supports.
Research note — draft for adversarial review; novelty not yet certified

