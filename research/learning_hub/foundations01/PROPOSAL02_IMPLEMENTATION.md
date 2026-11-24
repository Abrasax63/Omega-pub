# Implementation note (before execution)
Both arms use temperature 0.8 and no top-k/top-p filtering (top_k=0,
top_p=1). G restricts each next token to one of the allowed single-digit
IDs, samples renormalized model logits, records probability mass of the
allowed alphabet under the unconstrained distribution, and checks tokenizer
roundtrip. This is an explicit token-level intervention, not an equal-token
or equal-compute comparison. All labels computed after generation, no
training/holdout. The offline test enumerates all 13,824 syntactically valid
strings to check the representation against the established 2,320 classes.
