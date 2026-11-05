import Lean

/-
V19 locality — Lean formalization, first kernel.

This file formalizes both edge matchings, the periodic endpoints of invariant
edges, and a local obstruction to alternating forced chains of four edges.
The full P1--P4 component classification, visibility lemma, and L+2 shadow
theorem are not yet formalized.

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
  by_cases hvw : v = w
  · exact hvw
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
  exact False.elim (hvwColor sameColor)

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
The invariant relation is a matching in every coherent system.
-/
theorem v19_invariant_matching
    (T : α → α) (hcoh : V19Coherent T)
    {u v w : α}
    (huv : V19Invariant T u v)
    (huw : V19Invariant T u w) : v = w := by
  by_cases hvwEq : v = w
  · exact hvwEq
  rcases hcoh with ⟨color, hcolor⟩
  rcases huv.2 with ⟨huFix, hvFix⟩ | ⟨huSwap, hvSwap⟩
  · rcases huw.2 with ⟨huFix', hwFix⟩ | ⟨huSwap', hwSwap⟩
    · have hvw : V19Invariant T v w := ⟨hvwEq, Or.inl ⟨hvFix, hwFix⟩⟩
      have huvColor := hcolor (u := u) (v := v) (Or.inr huv)
      have huwColor := hcolor (u := u) (v := w) (Or.inr huw)
      have hvwColor := hcolor (u := v) (v := w) (Or.inr hvw)
      have sameColor : color v = color w :=
        bool_two_color_middle (color u) (color v) (color w) huvColor huwColor
      exact (hvwColor sameColor).elim
    · have hwEq : w = u := by
        calc
          w = T u := huSwap'.symm
          _ = u := huFix
      exact (huw.1 hwEq.symm).elim
  · rcases huw.2 with ⟨huFix', hwFix⟩ | ⟨huSwap', hwSwap⟩
    · have hvEq : v = u := by
        calc
          v = T u := huSwap.symm
          _ = u := huFix'
      exact (huv.1 hvEq.symm).elim
    · calc
        v = T u := huSwap.symm
        _ = w := huSwap'

/-- States on fixed points or 2-cycles, the only endpoints of I-edges. -/
def V19CorePeriodic (T : α → α) (x : α) : Prop :=
  T x = x ∨ ∃ y, T x = y ∧ T y = x ∧ y ≠ x

/-- Both endpoints of every invariant edge are fixed or on a 2-cycle. -/
theorem v19_invariant_endpoints_core_periodic
    (T : α → α) {u v : α} (h : V19Invariant T u v) :
    V19CorePeriodic T u ∧ V19CorePeriodic T v := by
  rcases h.2 with ⟨hu, hv⟩ | ⟨hu, hv⟩
  · exact ⟨Or.inl hu, Or.inl hv⟩
  · exact ⟨Or.inr ⟨v, hu, hv, h.1.symm⟩,
           Or.inr ⟨u, hv, hu, h.1⟩⟩

/--
A merge edge cannot join two distinct fixed/2-cycle states.
This is the local dynamical fact that prevents M-edges from joining
the periodic endpoints of I-edges.
-/
theorem v19_merge_not_both_core_periodic
    (T : α → α) {u v : α}
    (huv : V19Merge T u v)
    (hu : V19CorePeriodic T u)
    (hv : V19CorePeriodic T v) : False := by
  rcases hu with huFix | ⟨uNext, huNext, huBack, huNe⟩
  · rcases hv with hvFix | ⟨vNext, hvNext, hvBack, hvNe⟩
    · have huvEq : u = v := by
        calc
          u = T u := huFix.symm
          _ = T v := huv.2
          _ = v := hvFix
      exact huv.1 huvEq
    · have huNextEq : u = vNext := by
        calc
          u = T u := huFix.symm
          _ = T v := huv.2
          _ = vNext := hvNext
      have hTuv : T u = v := by
        calc
          T u = T vNext := congrArg T huNextEq
          _ = v := hvBack
      have huvEq : u = v := by
        calc
          u = T u := huFix.symm
          _ = v := hTuv
      exact huv.1 huvEq
  · rcases hv with hvFix | ⟨vNext, hvNext, hvBack, hvNe⟩
    · have huNextEq : uNext = v := by
        calc
          uNext = T u := huNext.symm
          _ = T v := huv.2
          _ = v := hvFix
      have hTvu : T v = u := by
        calc
          T v = T uNext := congrArg T huNextEq.symm
          _ = u := huBack
      have huvEq : u = v := by
        calc
          u = T u := huFix.symm
          _ = T v := huv.2
          _ = v := hvFix
      exact huv.1 huvEq
    · have hPartners : uNext = vNext := by
        calc
          uNext = T u := huNext.symm
          _ = T v := huv.2
          _ = vNext := hvNext
      have huvEq : u = v := by
        calc
          u = T uNext := huBack.symm
          _ = T vNext := congrArg T hPartners
          _ = v := hvBack
      exact huv.1 huvEq

/-- An alternating M-I-M-I chain of four edges is impossible. -/
theorem v19_no_alternating_MIMI
    (T : α → α) {x0 x1 x2 x3 x4 : α}
    (h01 : V19Merge T x0 x1)
    (h12 : V19Invariant T x1 x2)
    (h23 : V19Merge T x2 x3)
    (h34 : V19Invariant T x3 x4) : False := by
  have h2Periodic := (v19_invariant_endpoints_core_periodic T h12).2
  have h3Periodic := (v19_invariant_endpoints_core_periodic T h34).1
  exact v19_merge_not_both_core_periodic T h23 h2Periodic h3Periodic

/-- An alternating I-M-I-M chain of four edges is impossible. -/
theorem v19_no_alternating_IMIM
    (T : α → α) {x0 x1 x2 x3 x4 : α}
    (h01 : V19Invariant T x0 x1)
    (h12 : V19Merge T x1 x2)
    (h23 : V19Invariant T x2 x3)
    (h34 : V19Merge T x3 x4) : False := by
  have h1Periodic := (v19_invariant_endpoints_core_periodic T h01).2
  have h2Periodic := (v19_invariant_endpoints_core_periodic T h23).1
  exact v19_merge_not_both_core_periodic T h12 h1Periodic h2Periodic
