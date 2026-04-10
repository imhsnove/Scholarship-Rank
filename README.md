# Scholarship Shortlist — Merge Sort Visualiser
> CISC 121 · W26 Project

A Gradio app that ranks scholarship applicants using **Merge Sort** and walks the user through every split, comparison, and merge step so they can learn exactly how the algorithm works.

---

## Chosen Problem

**Problem 4 — Scholarship Shortlist.**  
Given a list of applicants (name, GPA, essay score, volunteer hours), compute a weighted final score and award scholarships to the top N students. The app sorts by final score (descending) and highlights winners.

---

## Chosen Algorithm — Merge Sort

Merge Sort was chosen because:
- The dataset has no pre-existing order (random order each run), so a divide-and-conquer approach that always runs in **O(n log n)** is ideal.
- Its step-by-step structure (split → sort halves → merge) maps cleanly onto a visual simulation — each stage is discrete and explainable.
- Unlike Quick Sort, it is **stable** and its worst-case performance is still O(n log n), which matters for a fair ranking system.

**Assumption:** GPA is on a 4.0 scale; essay scores are 0–100; volunteer hours are non-negative and capped at 200 for normalisation.

**Precondition:** At least 2 applicants must be entered. The app validates all inputs before sorting.

**What the user sees:**
-  **Split steps** — where the list is divided in half
-  **Compare steps** — which two applicants are being compared by score
-  **Pick steps** — which applicant was selected (higher score wins)
-  **Merge steps** — the newly merged (sorted) sublist

---

## Demo

<img width="653" height="810" alt="image" src="https://github.com/user-attachments/assets/67af3611-6fef-4044-9206-5c4e67c917b0" />



---

## Score Formula

```
Final Score = 0.50 × (GPA / 4.0 × 100)
            + 0.30 × Essay_Score
            + 0.20 × min(Volunteer_Hours / 200, 1) × 100
```

All three components are normalised to the same 0–100 scale before weighting, ensuring the formula is fair and interpretable.

---

## Problem Breakdown & Computational Thinking

### Decomposition
1. Parse and validate user input (one applicant per line)
2. Compute a weighted final score for each applicant
3. Run Merge Sort (descending by score), recording every step
4. Display the ranked table and the annotated step log

### Pattern Recognition
Merge Sort repeatedly:
- Splits a list at its midpoint
- Compares the front elements of two sorted halves
- Picks the larger one and advances that pointer
- Until one half is exhausted, then appends the remainder

### Abstraction
**Shown to user:** splits, comparisons, picks, and merges at the name level  
**Hidden from user:** array indices, pointer arithmetic, recursive call stack depth

### Algorithm Design (Input → Process → Output)

```
User types applicant rows
        │
        ▼
parse_applicants()  ← validates types, ranges, and line format
        │
        ▼
compute_score()     ← weighted formula per applicant
        │
        ▼
merge_sort()        ← records every step in `steps[]`
        │
   ┌────┴────┐
   ▼         ▼
render_results()  render_steps()
   │               │
   └──── Gradio HTML outputs ────┘
```

### Flowchart

```
START
  │
  ▼
Input: applicant list, top N
  │
  ▼
Validate input → Error? ──Yes──► Show error message → END
  │ No
  ▼
Compute the score for each applicant
  │
  ▼
merge_sort(list)
  │
  ├─ len ≤ 1? ──Yes──► return as-is
  │
  ▼
Split the list at the midpoint
  │
  ├─► merge_sort(left half)
  └─► merge_sort(right half)
          │
          ▼
      merge(left, right)
        ├─ Compare front elements
        ├─ Pick a higher score
        └─ Repeat until one half empty; append the rest
          │
          ▼
      Return sorted list
          │
          ▼
Display ranked table + step log
  │
 END
```

---

## Steps to Run (Local)

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/cisc121-scholarship-sort
cd cisc121-scholarship-rank

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python app.py
```

Then open `http://127.0.0.1:7860` in your browser.

---

## Hugging Face Link

https://huggingface.co/spaces/imhsnove/scholarship-rank

---

## Testing

| Test Case | Input | Expected | Actual | Pass? |
|---|---|---|---|---|
| Typical — 6 applicants, top 3 | See placeholder data | Top 3 by score highlighted | ✓ Correct ranking | ✅ |
| Edge — 2 applicants | Min valid input | 1 merge step, correct winner | ✓ | ✅ |
| Edge — all same score | 4 applicants, score = 75 | Stable order preserved | ✓ | ✅ |
| Edge — top N = total | top_n = number of applicants | All rows marked as awarded | ✓ | ✅ |
| Error — bad GPA | GPA = 5.0 | Friendly error message | "GPA must be between 0.0 and 4.0" | ✅ |
| Error — missing column | Only 3 values on a line | Friendly error | "expected 4 values …" | ✅ |
| Error — 1 applicant | Single line | Friendly error | "Please enter at least 2 applicants" | ✅ |
| Random data button | Click | 7 valid random rows inserted | ✓ | ✅ |

Validation used Python's `sorted()` to cross-check merge sort output on every test case.

---

## Author & Acknowledgment

- **Author:** Hassan Ebrahimi · Student ID: 20514196
- **Course:** CISC 121, Queen's University, W26
- **AI use:** Claude (Anthropic) was used at Level 4 to assist with code structure, CSS design, and README drafting. All algorithmic logic was reviewed and understood by the author.
- **References:**
  - CISC 121 lecture slides on Merge Sort
  - [VisuAlgo — Sorting](https://visualgo.net/en/sorting)
  - [Gradio documentation](https://gradio.app/docs)
