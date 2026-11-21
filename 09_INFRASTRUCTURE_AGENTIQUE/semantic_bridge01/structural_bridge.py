"""Deterministic, abstaining mathematical NL↔Lean *diagnostic signature* matcher.

This is NOT a formalizer, proof checker, semantic-equivalence decider or
trained model. It extracts reproducible, source-agnostic features; requires a
minimal amount of agreement before admitting a proposed correspondence; and
retains both source extracts and conflicting evidence for audit.

Crucial blind constraint: developed on pre-existing 8 examples from PR #227
BEFORE opening 12 reserved source texts in SEM-BRIDGE-01. Neither source IDs,
filenames, correct labels nor upstream pairing indices are matcher inputs.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
import unicodedata

MIN_SCORE=2.5
MIN_MARGIN=1.0

# Hand-written *prior* mathematical vocabulary from EXTERNAL-MEMORY-01 plus
# conventional mathematical notions. Entire dictionary is frozen before holdout.
# Each definition: NL patterns, Lean patterns, feature contribution (not a
# statistical probability). Formally explicit Lean operators are preferred.
CONCEPTS={
 "irreducible":(r"irreducib",r"\bIrreducible\b",3.2),
 "polynomial":(r"polynom|\bx\s*\^\s*\d",r"Polynomial|\bX\b",1.2),
 "prime":(r"\bprim(e|es)\b",r"\bPrime\b",2.6),
 "congruence":(r"congruen|\\equiv|\bmod(ulo)?\b",r"≡|\bMOD\b|\bMod\b",3.0),
 "divisibility":(r"divid(e|es|ing)|divisib|\\mid",r"∣|\bdvd\b",2.4),
 "coprime":(r"coprim|relatively prime|\(n\s*,\s*p",r"gcd|Coprime",2.0),
 "group":(r"\bgroup(s)?\b|\bG\b",r"\bGroup\b|\bSubgroup\b|IsSimpleGroup",1.4),
 "group_simple":(r"\bsimpl(e|icity)\b",r"IsSimpleGroup",3.3),
 "abelian":(r"abelian|commutativ",r"CommGroup|CommMonoid|IsMulCommutative|\ba\s*\*\s*b\s*≠\s*b\s*\*\s*a",2.5),
 "group_order":(r"infinite order|order of|\|G\||\border\s+\d",r"orderOf|\bcard\b|\bFintype\b",1.6),
 "isomorphism":(r"isomorph|\\simeq|\\cong",r"≃|Equiv|Iso",3.3),
 "linear_map":(r"linear (map|transformation|operator)|\\mathcal\{L\}",r"→ₗ|LinearMap|LinearEquiv",3.3),
 "scalar":(r"scalar|multipli(cation|ed|er) by some",r"•|smul|scalar",1.6),
 "dimension":(r"dimension|\\operatorname\{dim\}|\\dim\b|one-dimensional",r"finrank|Module\.rank|FiniteDimensional",2.4),
 "exists":(r"there exists|there is|some scalar|for some|\\exists",r"∃",1.1),
 "forall":(r"for all|every|each|\\forall",r"∀",0.9),
 "nonexist":(r"there is no|does not exist|no such",r"¬\s*∃|not_exists",2.1),
 "summability":(r"converge(s|nce)?|diverge(s|nce)?|summab|\\sum|\bseries\b",r"Summable|HasSum|tsum",2.8),
 "logarithm":(r"\\log|logarithm|natural log",r"log",1.4),
 "exponential":(r"\\exp|e\s*\^|exponential",r"Real\.exp|Complex\.exp|\bexp\b",1.6),
 "integral":(r"\\int|integral|integrat",r"∫|integral|Integrable",3.3),
 "cosine":(r"\\cos|cosine",r"cos",2.0),
 "sine":(r"\\sin|\bsine\b",r"sin",2.0),
 "limit":(r"limit|tends to|\\lim|as .*approach",r"Tendsto|Filter\.Tendsto|atTop|atBot",2.2),
 "continuous":(r"continu(ous|ity)",r"Continuous|continuous",3.0),
 "compact":(r"compact",r"IsCompact|CompactSpace",3.2),
 "connected":(r"connected",r"IsConnected|ConnectedSpace",3.2),
 "closed_set":(r"closed (set|subset)|is closed",r"IsClosed|ClosedEmbedding",2.8),
 "open_set":(r"open (set|subset)|is open",r"IsOpen|OpenEmbedding",2.8),
 "topology":(r"topolog",r"TopologicalSpace|Topological|Topology",1.9),
 "metric":(r"metric|distance",r"MetricSpace|dist\b",1.8),
 "norm":(r"norm|\\\|.*\\\|",r"\bnorm\b|Normed|‖",2.5),
 "inner_product":(r"inner product|orthogon",r"InnerProduct|inner|orthogonal",2.7),
 "matrix":(r"matri(x|ces)",r"Matrix|matrix",2.8),
 "determinant":(r"determinant|\\det",r"det\b|determinant",3.0),
 "ideal":(r"\bideal\b",r"\bIdeal\b",3.1),
 "ring":(r"\bring\b",r"\bRing\b|CommRing",1.7),
 "field":(r"\bfield\b|\\mathbb\{Q\}|\\mathbb\{R\}",r"\bField\b|\bℚ\b|\bℝ\b",1.4),
 "finite":(r"finite|\|G\||\bcardinal",r"Fintype|Finite|card\b",1.0),
 "injective":(r"injectiv|one.to.one",r"Injective",3.2),
 "surjective":(r"surjectiv|onto",r"Surjective",3.2),
 "bijective":(r"bijectiv|one.to.one correspond",r"Bijective|Equiv",3.2),
 "derivative":(r"derivativ|differentiab|\\frac\{d",r"HasDerivAt|deriv|Differentiable",3.2),
 "measurable":(r"measurab",r"Measurable|Measure",2.8),
 "set_union":(r"\\cup|union",r"∪|Set\.union",2.1),
 "set_intersection":(r"\\cap|intersection",r"∩|Set\.inter",2.1),
 "subset":(r"subset|\\subset",r"⊆|⊂|Set\.Subset",2.0),
 "homomorphism":(r"homomorph",r"MonoidHom|RingHom|LinearMap|→*",2.6),
 "kernel":(r"kernel",r"ker\b|LinearMap\.ker",2.7),
 "cyclic":(r"cyclic",r"IsCyclic|Cyclic",2.9),
 "normal_subgroup":(r"normal subgroup",r"Subgroup\.Normal|Normal",3.1),
 "inverse":(r"\binverse\b|invertib|reciprocal",r"IsUnit|IsInv|inv|⁻¹",2.0),
 "positive":(r"positive|greater than zero|a\s*>\s*0",r"0\s*<|0\s*≤|Pos|Nonneg",1.1),
 "less_equal":(r"\\leq|\\le|≤|at most|less than or equal",r"≤",1.1),
 "greater_equal":(r"\\geq|\\ge|≥|at least|greater than or equal",r"≥",1.1),
}

# Terms like "not simple", "diverges", "nonabelian" are negation-sensitive.
NEG_NL=(r"not simple|is not simple|nonabelian|non-abelian|diverg",)
NEG_LEAN=(r"¬|\bNot\b",)


def strip_lean_names(text:str)->str:
    # No family hint from teacher/exercise names or autogenerated identifiers.
    cleaned=re.sub(r"(?m)^theorem\s+[^\s:({]+", "theorem",text)
    return re.sub(r"(?m)^import\s+.*$", "", cleaned)


def numbers(text:str,language:str)->frozenset[str]:
    if language=="lean":
        text=strip_lean_names(text)
    else:
        # Remove LaTeX command names and \mathbb{Q} without synthesizing digits.
        pass
    # Limit numbers to literal numeral tokens, excluding numerals embedded in identifiers.
    return frozenset(re.findall(r"(?<![\w])\d+(?![\w])",text))


@dataclass(frozen=True)
class Signature:
    features:frozenset[str]
    explicit_numbers:frozenset[str]
    negated:bool


def signature(text:str,language:str)->Signature:
    if language not in ("nl","lean"):raise ValueError("unknown representation")
    if not isinstance(text,str) or not text.strip() or len(text)>50000:
        raise ValueError("missing or excessive mathematical text")
    s=strip_lean_names(text) if language=="lean" else text
    feats=frozenset(
        name for name,(nl,formal,weight) in CONCEPTS.items()
        if re.search(nl if language=="nl" else formal,s,
                     re.IGNORECASE if language=="nl" else 0)
    )
    patterns=NEG_NL if language=="nl" else NEG_LEAN
    is_neg=any(re.search(x,s,re.IGNORECASE) for x in patterns)
    return Signature(feats,numbers(s,language),is_neg)


def score(left:Signature,right:Signature)->dict:
    shared=left.features & right.features
    weights={k:CONCEPTS[k][2] for k in shared}
    concepts=round(sum(weights.values()),3)
    nums=sorted(left.explicit_numbers & right.explicit_numbers)
    # Numbers can independently occur in different mathematical contexts:
    # a small capped bonus is never sufficient for a standalone match.
    numeral_bonus=round(min(len(nums),3)*0.55,3)
    polarity_penalty=(1.4 if left.negated!=right.negated and shared else 0)
    # Penalize a candidate that explicitly matches contradictory themes;
    # avoid fabricating a "proof" from a global topical keyword.
    result=round(concepts+numeral_bonus-polarity_penalty,3)
    return {"score":result,"shared_features":sorted(shared),
            "shared_feature_weights":weights,
            "shared_numerals":nums,"polarity_penalty":polarity_penalty,
            "n_left_features":len(left.features),"n_right_features":len(right.features)}


def match(natural:str,formal_a:str,formal_b:str)->dict:
    """No access to source IDs, gold, theorem title, file path or metadata."""
    src=signature(natural,"nl")
    a=score(src,signature(formal_a,"lean"))
    b=score(src,signature(formal_b,"lean"))
    eligible_a=a["score"]>=MIN_SCORE and bool(a["shared_features"])
    eligible_b=b["score"]>=MIN_SCORE and bool(b["shared_features"])
    if eligible_a and (not eligible_b or a["score"]-b["score"]>=MIN_MARGIN):
        label="A";status="STRUCTURAL_MATCH_HEURISTIC"
    elif eligible_b and (not eligible_a or b["score"]-a["score"]>=MIN_MARGIN):
        label="B";status="STRUCTURAL_MATCH_HEURISTIC"
    elif eligible_a and eligible_b:
        label="NONE";status="AMBIGUOUS_ABSTAIN"
    else:
        label="NONE";status="UNSUPPORTED_ABSTAIN"
    return {
        "prediction":label,"status":status,"a":a,"b":b,
        "nl_signature":{"features":sorted(src.features),
                        "explicit_numbers":sorted(src.explicit_numbers),
                        "negated":src.negated},
        "min_score":MIN_SCORE,"min_margin":MIN_MARGIN,
        "is_math_proof":False,"semantic_equivalence_certified":False
    }


def guarded_proposal(model_reply:str,structural:dict)->dict:
    """Reject unsupported model claims. Never certify source fidelity."""
    p=model_reply.strip() if isinstance(model_reply,str) else None
    model_label=p if p in ("A","B","NONE") else None
    guard=structural["prediction"]
    if model_label is None:
        reason="MODEL_FORMAT_REJECTED"
    elif model_label==guard:
        reason="MODEL_AND_SIGNATURE_AGREE"
    else:
        reason="MODEL_AND_SIGNATURE_DISAGREE_OR_UNSUPPORTED"
    return {
        "prediction":guard,"reason":reason,
        "original_model_label":model_label,
        "semantic_equivalence_certified":False,
        "cannot_promote_to_proof":True,
    }
