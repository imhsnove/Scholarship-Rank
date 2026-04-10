"""
CISC 121 — Scholarship Shortlist
Merge Sort Visual Simulation
Author: [Your Name]

This app sorts scholarship applicants by a computed final score using
Merge Sort, and animates each step so students can see how the algorithm works.
"""

import gradio as gr
import random

# ─────────────────────────────────────────────
#  SCORE FORMULA  (explained in README)
#  Final Score = 0.50 × GPA_norm + 0.30 × Essay + 0.20 × Volunteer_norm
#  GPA is normalised to 0–100  (GPA/4.0 × 100)
#  Volunteer hours are capped at 200 and normalised to 0–100
# ─────────────────────────────────────────────
def compute_score(gpa: float, essay: float, volunteer: float) -> float:
    gpa_norm     = (gpa / 4.0) * 100          # 0–100
    vol_norm     = min(volunteer / 200, 1) * 100  # 0–100, capped at 200 hrs
    return round(0.50 * gpa_norm + 0.30 * essay + 0.20 * vol_norm, 2)


# ─────────────────────────────────────────────
#  MERGE SORT  — records every comparison step
# ─────────────────────────────────────────────
def merge_sort(arr, steps, depth=0):
    """
    Recursively splits arr in half, sorts each half, then merges.
    Every meaningful state (split / merge) is appended to `steps`.
    """
    if len(arr) <= 1:
        return arr

    mid   = len(arr) // 2
    left  = arr[:mid]
    right = arr[mid:]

    # Record the split
    steps.append({
        "type":    "split",
        "depth":   depth,
        "left":    [a["name"] for a in left],
        "right":   [a["name"] for a in right],
        "message": f"✂️  Split → Left: {[a['name'] for a in left]}  |  Right: {[a['name'] for a in right]}"
    })

    left  = merge_sort(left,  steps, depth + 1)
    right = merge_sort(right, steps, depth + 1)

    return merge(left, right, steps, depth)


def merge(left, right, steps, depth):
    """
    Merges two sorted halves, recording each comparison.
    """
    result, i, j = [], 0, 0

    while i < len(left) and j < len(right):
        # Compare the front of each half
        steps.append({
            "type":    "compare",
            "depth":   depth,
            "a":       left[i]["name"],
            "b":       right[j]["name"],
            "a_score": left[i]["score"],
            "b_score": right[j]["score"],
            "message": (
                f"🔍 Compare  {left[i]['name']} ({left[i]['score']})  vs  "
                f"{right[j]['name']} ({right[j]['score']})"
            )
        })

        if left[i]["score"] >= right[j]["score"]:   # higher score wins
            result.append(left[i])
            steps.append({
                "type":    "pick",
                "depth":   depth,
                "winner":  left[i]["name"],
                "message": f"   ↳ Picked {left[i]['name']} (higher or equal score)"
            })
            i += 1
        else:
            result.append(right[j])
            steps.append({
                "type":    "pick",
                "depth":   depth,
                "winner":  right[j]["name"],
                "message": f"   ↳ Picked {right[j]['name']} (higher score)"
            })
            j += 1

    # Append any remaining elements
    while i < len(left):
        result.append(left[i]);  i += 1
    while j < len(right):
        result.append(right[j]); j += 1

    steps.append({
        "type":    "merge",
        "depth":   depth,
        "merged":  [a["name"] for a in result],
        "message": f"🔗 Merged  → {[a['name'] for a in result]}"
    })

    return result


# ─────────────────────────────────────────────
#  PARSE raw textarea input
# ─────────────────────────────────────────────
def parse_applicants(raw: str):
    """
    Each line: Name, GPA, Essay(0-100), VolunteerHours
    Returns list of dicts or raises ValueError with a helpful message.
    """
    applicants = []
    for line_num, line in enumerate(raw.strip().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            raise ValueError(
                f"Line {line_num}: expected 4 values (Name, GPA, Essay, Volunteer) "
                f"but got {len(parts)}. → «{line}»"
            )
        name = parts[0]
        if not name:
            raise ValueError(f"Line {line_num}: Name cannot be empty.")
        try:
            gpa      = float(parts[1])
            essay    = float(parts[2])
            volunteer = float(parts[3])
        except ValueError:
            raise ValueError(
                f"Line {line_num}: GPA, Essay, and Volunteer must be numbers. "
                f"Got: {parts[1]!r}, {parts[2]!r}, {parts[3]!r}"
            )
        if not (0.0 <= gpa <= 4.0):
            raise ValueError(f"Line {line_num}: GPA must be between 0.0 and 4.0. Got {gpa}.")
        if not (0.0 <= essay <= 100.0):
            raise ValueError(f"Line {line_num}: Essay score must be 0–100. Got {essay}.")
        if volunteer < 0:
            raise ValueError(f"Line {line_num}: Volunteer hours cannot be negative. Got {volunteer}.")

        applicants.append({
            "name":      name,
            "gpa":       gpa,
            "essay":     essay,
            "volunteer": volunteer,
            "score":     compute_score(gpa, essay, volunteer)
        })

    if len(applicants) < 2:
        raise ValueError("Please enter at least 2 applicants to run the sort.")
    return applicants


# ─────────────────────────────────────────────
#  BUILD HTML output blocks
# ─────────────────────────────────────────────
MEDAL = ["🥇", "🥈", "🥉"]

def render_results(sorted_applicants, top_n):
    rows = ""
    for rank, a in enumerate(sorted_applicants):
        medal  = MEDAL[rank] if rank < 3 else f"#{rank+1}"
        hl     = " winner-row" if rank < top_n else ""
        badge  = "<span class='badge'>Awarded ✓</span>" if rank < top_n else ""
        rows += f"""
        <tr class='data-row{hl}'>
          <td class='rank-cell'>{medal}</td>
          <td>{a['name']}</td>
          <td>{a['gpa']:.2f}</td>
          <td>{a['essay']:.1f}</td>
          <td>{a['volunteer']:.0f} hrs</td>
          <td><strong>{a['score']:.2f}</strong></td>
          <td>{badge}</td>
        </tr>"""

    return f"""
    <div class='results-wrap'>
      <h3 class='section-label'>Final Rankings</h3>
      <p class='subtitle'>Top <strong>{top_n}</strong> applicant(s) awarded the scholarship</p>
      <table class='results-table'>
        <thead>
          <tr>
            <th>Rank</th><th>Name</th><th>GPA</th>
            <th>Essay</th><th>Volunteer</th><th>Score</th><th>Status</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <p class='formula-note'>
        Score = 50% GPA (normalised) + 30% Essay + 20% Volunteer (capped 200 hrs, normalised)
      </p>
    </div>"""


def render_steps(steps):
    items = ""
    for s in steps:
        t = s["type"]
        if t == "split":
            items += f"<li class='step-split'>{s['message']}</li>"
        elif t == "compare":
            items += f"<li class='step-compare'>{s['message']}</li>"
        elif t == "pick":
            items += f"<li class='step-pick'>{s['message']}</li>"
        elif t == "merge":
            items += f"<li class='step-merge'>{s['message']}</li>"

    return f"""
    <div class='steps-wrap'>
      <h3 class='section-label'>Merge Sort — Step by Step</h3>
      <ol class='step-list'>{items}</ol>
    </div>"""


# ─────────────────────────────────────────────
#  GENERATE random sample data
# ─────────────────────────────────────────────
FIRST = ["Alice","Ben","Clara","David","Emma","Farid","Grace","Hana","Ivan","Julia"]
LAST  = ["Smith","Chen","Patel","Johnson","Lee","Garcia","Nguyen","Kim","Brown","Wilson"]

def random_applicants(n=6):
    names = random.sample([f"{f} {l}" for f in FIRST for l in LAST], n)
    lines = []
    for name in names:
        gpa  = round(random.uniform(2.0, 4.0), 2)
        ess  = round(random.uniform(50, 100), 1)
        vol  = random.randint(0, 200)
        lines.append(f"{name}, {gpa}, {ess}, {vol}")
    return "\n".join(lines)


# ─────────────────────────────────────────────
#  MAIN sort function called by Gradio
# ─────────────────────────────────────────────
def run_sort(raw_input: str, top_n: int):
    try:
        applicants = parse_applicants(raw_input)
    except ValueError as e:
        error_html = f"""
        <div class='error-box'>
          <span class='error-icon'>⚠</span>
          <span>{e}</span>
        </div>"""
        return error_html, ""

    top_n = max(1, min(int(top_n), len(applicants)))

    steps = []
    sorted_applicants = merge_sort(applicants, steps)

    results_html = render_results(sorted_applicants, top_n)
    steps_html   = render_steps(steps)
    return results_html, steps_html


# ─────────────────────────────────────────────
#  CUSTOM CSS — macOS-inspired minimal design
# ─────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body, .gradio-container {
  font-family: 'DM Sans', sans-serif;
  background: #f5f5f7;
  color: #1d1d1f;
  min-height: 100vh;
}

.gradio-container { max-width: 960px !important; margin: 0 auto; padding: 40px 24px; }

/* ── Header ── */
.app-header {
  text-align: center;
  padding: 48px 0 36px;
  border-bottom: 1px solid #d2d2d7;
  margin-bottom: 36px;
}
.app-header h1 {
  font-size: 2.4rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: #1d1d1f;
}
.app-header p {
  margin-top: 8px;
  color: #6e6e73;
  font-size: 1rem;
  font-weight: 400;
}

/* ── Panels ── */
.panel {
  background: #ffffff;
  border-radius: 18px;
  padding: 28px 32px;
  border: 1px solid #e0e0e5;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  margin-bottom: 20px;
}

/* ── Gradio overrides ── */
.gr-button {
  border-radius: 980px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  padding: 10px 22px !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
}
.gr-button.primary {
  background: #0071e3 !important;
  color: white !important;
  border: none !important;
}
.gr-button.primary:hover { background: #0077ed !important; box-shadow: 0 4px 12px rgba(0,113,227,0.35) !important; }
.gr-button.secondary {
  background: transparent !important;
  color: #0071e3 !important;
  border: 1.5px solid #0071e3 !important;
}
.gr-button.secondary:hover { background: rgba(0,113,227,0.06) !important; }

textarea, input[type=number] {
  font-family: 'DM Mono', monospace !important;
  font-size: 0.85rem !important;
  border-radius: 10px !important;
  border: 1px solid #d2d2d7 !important;
  background: #fafafa !important;
  padding: 14px !important;
  transition: border-color 0.15s !important;
  color: #1d1d1f !important;
}
textarea:focus, input[type=number]:focus {
  border-color: #0071e3 !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(0,113,227,0.15) !important;
}

label span { font-weight: 500 !important; font-size: 0.85rem !important; color: #3a3a3c !important; }

/* ── Results HTML ── */
.results-wrap, .steps-wrap { font-family: 'DM Sans', sans-serif; }

.section-label {
  font-size: 1.05rem;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 4px;
  letter-spacing: -0.01em;
}
.subtitle { font-size: 0.85rem; color: #6e6e73; margin-bottom: 18px; }

.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.results-table th {
  text-align: left;
  font-weight: 500;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6e6e73;
  padding: 8px 12px;
  border-bottom: 1px solid #e0e0e5;
}
.data-row td {
  padding: 11px 12px;
  border-bottom: 1px solid #f0f0f5;
  color: #3a3a3c;
  vertical-align: middle;
}
.data-row:last-child td { border-bottom: none; }
.winner-row { background: #f0f7ff; }
.winner-row td { color: #1d1d1f !important; }
.rank-cell { font-size: 1.1rem; }

.badge {
  background: #e8f4e8;
  color: #1a7a1a;
  border-radius: 980px;
  padding: 2px 10px;
  font-size: 0.75rem;
  font-weight: 600;
}

.formula-note {
  margin-top: 16px;
  font-size: 0.78rem;
  color: #8e8e93;
  font-family: 'DM Mono', monospace;
}

/* ── Steps ── */
.step-list {
  list-style: none;
  font-family: 'DM Mono', monospace;
  font-size: 0.8rem;
  line-height: 1.8;
  counter-reset: step-counter;
}
.step-list li {
  padding: 3px 0 3px 0;
  border-bottom: 1px solid #f5f5f7;
  color: #3a3a3c;
}
.step-split  { color: #6e3de8 !important; }
.step-compare { color: #0071e3 !important; }
.step-pick   { color: #1a7a1a !important; padding-left: 12px !important; }
.step-merge  { color: #c75000 !important; font-weight: 500 !important; }

/* ── Error ── */
.error-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #fff2f2;
  border: 1px solid #ffd0d0;
  border-radius: 10px;
  padding: 14px 18px;
  color: #c0392b;
  font-size: 0.88rem;
}
.error-icon { font-size: 1.2rem; }

/* ── Instructions ── */
.instructions {
  background: #f5f5f7;
  border-radius: 12px;
  padding: 16px 20px;
  font-size: 0.82rem;
  color: #6e6e73;
  line-height: 1.7;
  border: 1px solid #e0e0e5;
  margin-bottom: 12px;
}
.instructions strong { color: #3a3a3c; }
.instructions code {
  background: #e8e8ed;
  border-radius: 4px;
  padding: 1px 5px;
  font-family: 'DM Mono', monospace;
  font-size: 0.8rem;
}
"""

# ─────────────────────────────────────────────
#  GRADIO UI
# ─────────────────────────────────────────────
PLACEHOLDER = """Alice Wong, 3.92, 88, 120
Ben Carter, 3.45, 76, 200
Clara Diaz, 3.78, 92, 85
David Kim, 2.95, 65, 150
Emma Patel, 4.00, 95, 60
Farid Hassan, 3.60, 80, 170"""

with gr.Blocks(css=CSS, title="Scholarship Shortlist — Merge Sort") as demo:

    gr.HTML("""
    <div class='app-header'>
      <h1>Scholarship Shortlist</h1>
      <p>Merge Sort Visual Simulation &nbsp;·&nbsp; CISC 121</p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=5):
            gr.HTML("""
            <div class='instructions'>
              <strong>How to enter applicants</strong><br>
              One applicant per line, comma-separated:<br>
              <code>Name, GPA (0–4.0), Essay Score (0–100), Volunteer Hours</code><br><br>
              <strong>Score formula:</strong>
              50% GPA · 30% Essay · 20% Volunteer (capped at 200 hrs)
            </div>
            """)
            applicant_input = gr.Textbox(
                label="Applicants",
                placeholder=PLACEHOLDER,
                lines=9,
                value=PLACEHOLDER
            )

        with gr.Column(scale=2):
            top_n_input = gr.Number(
                label="Number of scholarships to award (Top N)",
                value=3,
                minimum=1,
                precision=0
            )
            gr.HTML("<br>")
            sort_btn   = gr.Button("Run Merge Sort →", variant="primary")
            random_btn = gr.Button("Generate Random Data", variant="secondary")

    results_out = gr.HTML(label="Results")
    steps_out   = gr.HTML(label="Algorithm Steps")

    # ── Button logic ──
    sort_btn.click(
        fn=run_sort,
        inputs=[applicant_input, top_n_input],
        outputs=[results_out, steps_out]
    )

    random_btn.click(
        fn=lambda: random_applicants(7),
        inputs=[],
        outputs=[applicant_input]
    )

if __name__ == "__main__":
    demo.launch()
