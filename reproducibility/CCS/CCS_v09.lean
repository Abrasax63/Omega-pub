-- CCS v0.9: theorem for the fixed, explicitly enumerated example.
-- No sorry/axiom. Requires Lean 4 to check.
def sourceDomain : List Nat := [0, 1, 2, 3]
def targetDomain : List Nat := [10, 11, 12, 13]
def f (x : Nat) : Nat := x + 10
def h1 (x : Nat) : Prop := x > 0
def h2 (y : Nat) : Prop := y > 10
def p1 (x : Nat) : Prop := x % 2 = 0
def p2 (y : Nat) : Prop := y % 2 = 0

theorem ccs_mapping : sourceDomain.map f = targetDomain := by decide
theorem ccs_hypothesis :
    ∀ x ∈ sourceDomain, (h1 x ↔ h2 (f x)) := by decide
theorem ccs_conclusion :
    ∀ x ∈ sourceDomain, h1 x → (p1 x ↔ p2 (f x)) := by decide
theorem ccs_statement_equiv :
    ((∀ x ∈ sourceDomain, h1 x → p1 x) ↔
     (∀ y ∈ targetDomain, h2 y → p2 y)) := by decide