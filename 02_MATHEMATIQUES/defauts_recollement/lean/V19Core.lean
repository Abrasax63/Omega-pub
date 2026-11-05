/-
V19 locality — Lean formalization, first kernel.

This file formalizes only the elementary matching consequence for merge edges.
It does NOT formalize the invariant-edge matching lemma, the P1--P4 component
classification, the visibility lemma, or the L+2 shadow theorem.

Compile from this directory with:
  lean V19Core.lean
-/

universe u

variable {α : Type u}

def V19Merge (T : α → α) (u v : α) : Prop :=
  u ≠ v ∧ T u = T v

def V19Invariant (T : α → α) (u v : α) : Prop :=
  u ≠ v ∧
    ((T u = u ∧ T v = v) ∨ (T u = v ∧ T v = u))

def V19Coherent (T : α → α) : Prop :=
  ∃ color : α → Bool,
    ∀ ⦃u v : α⦄,
      (V19Merge T u v ∨ V19Invariant T u v) →
      color u ≠ color v

private theorem bool_two_color_middle
    (a b c : Bool) (hab : a ≠ b) (hac : a ≠ c) : b = c := by
  cases a <;> cases b <;> cases c <;> simp_all

/--
A coherent forced-constraint graph cannot contain two distinct merge
neighbors at one vertex. Equivalently, every fibre of T has size at most two.
-/
theorem v19_merge_matching
    (T : α → α) (hcoh : V19Coherent T)
    {u v w : α}
    (huv : V19Merge T u v)
    (huw : V19Merge T u w) : v = w := by
  rcases hcoh with ⟨color, hcolor⟩
  by_contra hvw
  have hvwMerge : V19Merge T v w := by
    refine ⟨hvw, ?_⟩
    calc
      T v = T u := huv.2.symm
      _ = T w := huw.2
  have huvColor := hcolor (u := u) (v := v) (Or.inl huv)
  have huwColor := hcolor (u := u) (v := w) (Or.inl huw)
  have hvwColor := hcolor (u := v) (v := w) (Or.inl hvwMerge)
  have sameColor : color v = color w :=
    bool_two_color_middle (color u) (color v) (color w) huvColor huwColor
  exact hvwColor sameColor

/--
No three distinct states can have the same image in a coherent system.
This is the direct fibre-cardinality form of the merge-matching theorem.
-/
theorem v19_no_three_preimages
    (T : α → α) (hcoh : V19Coherent T)
    {u v w : α}
    (huv : u ≠ v) (huw : u ≠ w) (hvw : v ≠ w)
    (hTu : T u = T v) (hTw : T u = T w) : False := by
  have hmergeUV : V19Merge T u v := ⟨huv, hTu⟩
  have hmergeUW : V19Merge T u w := ⟨huw, hTw⟩
  have hEq := v19_merge_matching T hcoh hmergeUV hmergeUW
  exact hvw hEq


/--
The invariant relation is a matching in every coherent system:
a fixed point can only be paired with another fixed point, of which
there is at most one; a point on a 2-cycle can only be paired with
its unique cycle partner.
-/
theorem v19_invariant_matching
    (T : α → α) (hcoh : V19Coherent T)
    {u v w : α}
    (huv : V19Invariant T u v)
    (huw : V19Invariant T u w) : v = w := by
  rcases hcoh with ⟨color, hcolor⟩
  rcases huv.2 with ⟨huFix, hvFix⟩ | ⟨huSwap, hvSwap⟩
  · rcases huw.2 with ⟨huFix', hwFix⟩ | ⟨huSwap', hwSwap⟩
    · have hvw : V19Invariant T v w := ⟨by
        intro h
        subst w
        exact huw.1 rfl, Or.inl ⟨hvFix, hwFix⟩⟩
      have huvColor := hcolor (u := u) (v := v) (Or.inr huv)
      have huwColor := hcolor (u := u) (v := w) (Or.inr huw)
      have hvwColor := hcolor (u := v) (v := w) (Or.inr hvw)
      have sameColor : color v = color w :=
        bool_two_color_middle (color u) (color v) (color w) huvColor huwColor
      exact False.elim (hvwColor sameColor)
    · have hwEq : w = u := by
        calc
          w = T u := huSwap'.symm
          _ = u := huFix
      exact False.elim (huw.1 hwEq.symm)
  · rcases huw.2 with ⟨huFix', hwFix⟩ | ⟨huSwap', hwSwap⟩
    · have hvEq : v = u := by
        calc
          v = T u := huSwap.symm
          _ = u := huFix'
      exact False.elim (huv.1 hvEq.symm)
    · calc
        v = T u := huSwap.symm
        _ = w := huSwap'

/-- Every invariant edge has periodic endpoints (period 1 or 2). -/
theorem v19_invariant_endpoints_periodic
    (T : α → α) {u v : α} (h : V19Invariant T u v) :
    (∃ n : Nat, n > 0 ∧ (T^[n]) u = u) ∧
    (∃ n : Nat, n > 0 ∧ (T^[n]) v = v) := by
  rcases h.2 with ⟨hu, hv⟩ | ⟨hu, hv⟩
  · exact ⟨⟨1, by omega, by simpa using hu⟩,
           ⟨1, by omega, by simpa using hv⟩⟩
  · refine ⟨⟨2, by omega, ?_⟩, ⟨2, by omega, ?_⟩⟩
    · simp [Function.iterate_succ_apply', hu, hv]
    · simp [Function.iterate_succ_apply', hv, hu]
