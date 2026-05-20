#!/usr/bin/env python3
"""generate_slides.py

Extracts circuit figures from exam_sample.pdf using PyMuPDF, then generates
exam3_slides.qmd — a Quarto RevealJS answer-key slide deck for EEE 141 Exam 3.

Answer reveal animation:
  - Wrong answers: .fragment .semi-fade-out (dim to ~50% on first keypress)
  - Correct answer: no fragment (stays at full opacity)
"""

import os
import fitz  # PyMuPDF

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = "/workspaces/07_Quarto_Notes/slides/_hide_131_exam"
PDF  = f"{BASE}/exam_sample.pdf"
FIGS = f"{BASE}/figures"
QMD  = f"{BASE}/exam3_slides.qmd"
CSS  = f"{BASE}/exam3_styles.css"

os.makedirs(FIGS, exist_ok=True)

# ── Figure extraction ─────────────────────────────────────────────────────────
# Each entry: (0-indexed page, (x0,y0,x1,y1) in PDF pts, filename, description)
FIGURE_REGIONS = [
    (0, (345, 265, 523, 445), "fig_q3.png",    "NPN series-shunt circuit (Q3)"),
    (0, (63,  388, 345, 607), "fig_q4.png",    "Multi-topology feedback circuit (Q4)"),
    (1, (121, 219, 474, 508), "fig_q8_12.png", "MOSFET+BJT amplifier + param table (Q8-12)"),
    (2, (370, 288, 513, 444), "fig_q17_18.png","Op-amp series-series circuit (Q17-18)"),
    (2, (49,  503, 287, 672), "fig_q19_22.png","Current-mirror shunt-series circuit (Q19-22)"),
    (3, (342, 126, 531, 267), "fig_q23_26.png","BJT shunt-shunt circuit (Q23-26)"),
    (4, (243, 132, 551, 244), "fig_q32_34.png","Two-stage Miller-compensated amp (Q32-34)"),
]

PAD   = 12    # padding around crop rect (PDF points)
SCALE = 2.5   # render scale for clarity

doc = fitz.open(PDF)
print("── Extracting figures ───────────────────────────────────────────")
for page_idx, (x0, y0, x1, y1), fname, desc in FIGURE_REGIONS:
    page = doc[page_idx]
    clip = fitz.Rect(
        max(0.0,             x0 - PAD),
        max(0.0,             y0 - PAD),
        min(page.rect.width, x1 + PAD),
        min(page.rect.height,y1 + PAD),
    )
    pix = page.get_pixmap(
        matrix=fitz.Matrix(SCALE, SCALE),
        clip=clip,
        colorspace=fitz.csRGB,
    )
    out = f"{FIGS}/{fname}"
    pix.save(out)
    print(f"  {fname}  {pix.width}×{pix.height}px  — {desc}")
doc.close()
print()

# ── Question data ─────────────────────────────────────────────────────────────
# (number, question_markdown, {key: text}, correct_set, fig_relpath | None)
# fig_relpath is relative to the QMD (same directory → "figures/fig_qN.png")

QUESTIONS = [
    (1,
     "If an amplifier has a forward gain of 400 and the feedback ratio is 0.1, "
     "find the overall gain with negative feedback.",
     {'a': '6.75',  'b': '7.75',   'c': '9.75',   'd': '10.75'},
     {'c'}, None),

    (2,
     "A shunt-series feedback amplifier has a voltage gain with feedback of 83.33 "
     "and feedback factor of 0.01. What is the voltage gain without feedback?",
     {'a': '200', 'b': '300', 'c': '400', 'd': '500'},
     {'d'}, None),

    (3,
     "What is the feedback configuration of the circuit on the right?",
     {'a': 'Shunt-Series', 'b': 'Series-Series',
      'c': 'Series-Shunt', 'd': 'Shunt-Shunt'},
     {'c'}, "figures/fig_q3.png"),

    (4,
     "What feedback circuits are present in the circuit on the left?",
     {'a': 'shunt-shunt and shunt-series', 'b': 'shunt-shunt only',
      'c': 'shunt-series only',           'd': 'shunt-shunt and series-series'},
     {'a'}, "figures/fig_q4.png"),

    (5,
     "Consider a series-series feedback network: amplifier gain = 100, "
     "feedback factor = 5, input voltage = 4 V, input current = 2 mA. "
     "Find the input resistance of the network.",
     {'a': '1002 k\u03a9', 'b': '2 k\u03a9', 'c': '1.002 k\u03a9', 'd': '2000 k\u03a9'},
     {'a'}, None),

    (6,
     "What happens to the impedances of an amplifier where the feedback is "
     "connected **in parallel with the output** and **in series with the input**? "
     "*(Select all that apply.)*",
     {'a': 'Its input impedance increases',  'b': 'Its output impedance increases',
      'c': 'Its output impedance decreases', 'd': 'Its input impedance decreases'},
     {'a', 'c'}, None),

    (7,
     "The negative feedback in an amplifier leads to which one of the following?",
     {'a': 'Increase in current gain', 'b': 'Increase in voltage gain',
      'c': 'Decrease in voltage gain', 'd': 'Decreases in bandwidth'},
     {'c'}, None),

    (8,
     "**[Q8\u201312: Refer to the circuit shown.]** "
     "What is the value of the open-loop input resistance?",
     {'a': '300 \u03a9', 'b': '400 \u03a9', 'c': '500 \u03a9', 'd': '600 \u03a9'},
     {'c'}, "figures/fig_q8_12.png"),

    (9,
     "What is the value of the open-loop transconductance?",
     {'a': '\u221233.7 S', 'b': '\u221235.7 S',
      'c': '\u221237.7 S', 'd': '\u221239.7 S'},
     {'b'}, "figures/fig_q8_12.png"),

    (10,
     "Determine the value of the feedback factor.",
     {'a': '\u22120.1', 'b': '\u22120.2', 'c': '\u22120.3', 'd': '\u22120.4'},
     {'d'}, "figures/fig_q8_12.png"),

    (11,
     "What is the value of the open-loop gain?",
     {'a': '17,850', 'b': '\u221217,850', 'c': '15,320', 'd': '\u221215,320'},
     {'b'}, "figures/fig_q8_12.png"),

    (12,
     "What is the value of the closed-loop gain?",
     {'a': '\u22121.3998', 'b': '1.3998', 'c': '2.4997', 'd': '\u22122.4997'},
     {'d'}, "figures/fig_q8_12.png"),

    (13,
     "Which of the following best describes the signal and feedback type "
     "in a shunt-shunt feedback amplifier?",
     {'a': 'Voltage input, voltage feedback', 'b': 'Current input, voltage feedback',
      'c': 'Voltage input, current feedback', 'd': 'Current input, current feedback'},
     {'d'}, None),

    (14,
     "Identify the amplifier property that is applicable to a current amplifier.",
     {'a': 'High input impedance', 'b': 'High efficiency',
      'c': 'Low input impedance',  'd': 'Low output impedance'},
     {'c'}, None),

    (15,
     "A shunt-series topology is a ______ amplifier with feedback.",
     {'a': 'current', 'b': 'transconductance', 'c': 'voltage', 'd': 'transresistance'},
     {'a'}, None),

    (16,
     "A transconductance amplifier should have:",
     {'a': 'Low output impedance', 'b': 'High efficiency',
      'c': 'Low input impedance',  'd': 'High output impedance'},
     {'d'}, None),

    (17,
     "**[Q17\u201318: R_L = 1000 \u03a9, R_E = 2500 \u03a9.]** "
     "The circuit shown is an example of what type of amplifier?",
     {'a': 'Series\u2013Series', 'b': 'Shunt\u2013Series',
      'c': 'Shunt\u2013Shunt',   'd': 'Series\u2013Shunt'},
     {'a'}, "figures/fig_q17_18.png"),

    (18,
     "Determine the feedback factor F for the circuit.",
     {'a': '2500 \u03a9', 'b': '1000 \u03a9', 'c': '3500 \u03a9', 'd': '714 \u03a9'},
     {'a'}, "figures/fig_q17_18.png"),

    (19,
     "**[Q19\u201322: Refer to the circuit shown.]** "
     "The circuit is an example of what type of amplifier?",
     {'a': 'Series\u2013Series', 'b': 'Shunt\u2013Series',
      'c': 'Shunt\u2013Shunt',   'd': 'Series\u2013Shunt'},
     {'b'}, "figures/fig_q19_22.png"),

    (20,
     "What is the input resistance of the feedback network in this circuit?",
     {'a': '138.46 \u03a9', 'b': '500 \u03a9',
      'c': '115.38 \u03a9', 'd': '650 \u03a9'},
     {'a'}, "figures/fig_q19_22.png"),

    (21,
     "What is the output resistance of the feedback network in this circuit?",
     {'a': '138.46 \u03a9', 'b': '500 \u03a9',
      'c': '115.38 \u03a9', 'd': '650 \u03a9'},
     {'c'}, "figures/fig_q19_22.png"),

    (22,
     "What is the feedback factor F in this circuit?",
     {'a': '34.62', 'b': '80', 'c': '40', 'd': '46.15'},
     {'d'}, "figures/fig_q19_22.png"),

    (23,
     "**[Q23\u201326: Refer to the circuit on the right.]** "
     "The circuit is an example of what type of amplifier?",
     {'a': 'Series\u2013Series', 'b': 'Shunt\u2013Series',
      'c': 'Shunt\u2013Shunt',   'd': 'Series\u2013Shunt'},
     {'c'}, "figures/fig_q23_26.png"),

    (24,
     "This amplifier is an example of a:",
     {'a': 'current amplifier',        'b': 'transconductance amplifier',
      'c': 'voltage amplifier',         'd': 'transresistance amplifier'},
     {'d'}, "figures/fig_q23_26.png"),

    (25,
     "If R_S = 1000 \u03a9 and R_f = 3000 \u03a9, F is equal to:",
     {'a': '1000', 'b': '0.001', 'c': '3000', 'd': '0.0003'},
     {'b'}, "figures/fig_q23_26.png"),

    (26,
     "If R_S = 1000 \u03a9 and R_f = 3000 \u03a9, the output resistance is:",
     {'a': '4000 \u03a9', 'b': '1000 \u03a9', 'c': '3000 \u03a9', 'd': '0.001 \u03a9'},
     {'b'}, "figures/fig_q23_26.png"),

    (27,
     "Consider the following statements:\n\n"
     "- **I.** A single-pole forward path gives a stable loop gain for a passive feedback implementation.\n"
     "- **II.** A feedback system with forward-path poles results in only zeroes in the closed-loop system.\n"
     "- **III.** A right-half-plane pole in the loop gain produces a stable oscillation at the output.\n"
     "- **IV.** The dominant pole is the \u22123 dB bandwidth for a single-pole system.\n\n"
     "Which statement(s) is/are **always TRUE**?",
     {'a': 'I, II, III', 'b': 'I, II, IV', 'c': 'II, III', 'd': 'I, IV'},
     {'d'}, None),

    (28,
     "**[Q28\u201331: A_v = 20,000 V/V; poles at 100 krad/s, 3 Mrad/s, 5 Mrad/s; F = 0.5]**\n\n"
     "What is the unity-gain frequency \u03c9_u of the loop gain?",
     {'a': '31.07 Mrad/s', 'b': '24.66 Mrad/s',
      'c': '19.57 Mrad/s', 'd': '39.15 Mrad/s'},
     {'b'}, None),

    (29,
     "Calculate the phase margin of the loop-gain.",
     {'a': '\u221271.37\u00b0', 'b': '75.16\u00b0',
      'c': '\u221275.16\u00b0', 'd': '71.37\u00b0'},
     {'a'}, None),

    (30,
     "Narrowband compensation is employed. Calculate the new dominant pole "
     "if the target \u03c9_u = 1.4 Mrad/s.",
     {'a': '190 rad/s', 'b': '310 rad/s', 'c': '240 rad/s', 'd': '140 rad/s'},
     {'d'}, None),

    (31,
     "Calculate the new phase margin after narrowbanding compensation.",
     {'a': '64.98\u00b0', 'b': '53.43\u00b0', 'c': '49.35\u00b0', 'd': '69.07\u00b0'},
     {'c'}, None),

    (32,
     "**[Q32\u201334: Two-stage amplifier, C_f = 2 pF.]**\n\n"
     "What is the equivalent capacitance seen at the input of the second stage?",
     {'a': '15.92 pF', 'b': '2.02 nF', 'c': '2.00 nF', 'd': '17.92 pF'},
     {'b'}, "figures/fig_q32_34.png"),

    (33,
     "Determine the dominant pole of the Miller-compensated circuit.",
     {'a': '7.96 Hz', 'b': '6.28 kHz', 'c': '50 Hz', 'd': '999.72 Hz'},
     {'a'}, "figures/fig_q32_34.png"),

    (34,
     "Ignoring any zeroes of the amplifier, calculate the phase margin.",
     {'a': '59.92\u00b0', 'b': '57.26\u00b0', 'c': '51.59\u00b0', 'd': '55.69\u00b0'},
     {'c'}, "figures/fig_q32_34.png"),

    (35,
     "In a Miller-compensated circuit, what is the trade-off when increasing C_m?",
     {'a': 'Higher power consumption vs. higher phase margin',
      'b': 'Higher gain vs. lower bandwidth',
      'c': 'Lower unity-gain frequency vs. higher stability',
      'd': 'Lower phase margin vs. higher bandwidth'},
     {'c'}, None),

    (36,
     "In a compensated two-pole system, what is the approximate phase margin "
     "if the second pole lies at 20\u00d7 the unity-gain frequency?",
     {'a': '90\u00b0', 'b': '60\u00b0', 'c': '45\u00b0', 'd': '0\u00b0'},
     {'a'}, None),

    (37,
     "Which of the following is true regarding dominant pole compensation?",
     {'a': 'Improves gain at high frequencies',
      'b': 'Reduces the effect of higher frequency poles',
      'c': 'Decreases the other poles in the system',
      'd': 'Increases phase margin by adding LHP zeroes'},
     {'b'}, None),

    (38,
     "An underdamped two-pole system has:",
     {'a': 'Real negative poles',       'b': 'Real and complex poles',
      'c': 'Real positive poles',        'd': 'Complex conjugate poles'},
     {'d'}, None),

    (39,
     "In a feedback closed-loop system, stability problems arise when:",
     {'a': 'Feedback becomes positive at high frequencies',
      'b': 'Phase margin exceeds 90\u00b0',
      'c': 'Loop gain is too small',
      'd': 'Closed-loop gain bandwidth becomes too large'},
     {'a'}, None),

    (40,
     "A feedback amplifier has an open-loop DC gain of 100 dB and poles "
     "at 1 kHz and 1 MHz. What is the gain-bandwidth product (GBW)?",
     {'a': '100 kHz', 'b': '1 MHz', 'c': '10 MHz', 'd': '100 MHz'},
     {'d'}, None),

    (41,
     "A feedback amplifier has poles at 10 kHz and 1 MHz. "
     "If the phase shift at 1 MHz is 135\u00b0, what is the phase margin?",
     {'a': '0\u00b0', 'b': '45\u00b0', 'c': '90\u00b0', 'd': '180\u00b0'},
     {'b'}, None),

    (42,
     "If the closed-loop bandwidth of a unity-gain feedback amplifier is 100 kHz "
     "and the DC open-loop gain is 100, what is the open-loop GBW product?",
     {'a': '100 Hz', 'b': '1 kHz', 'c': '100 kHz', 'd': '1 MHz'},
     {'c'}, None),

    (43,
     "The transfer function is A(s) = 10\u2074 / [(1+s/10\u2075)(1+s/10\u2076)]. "
     "A capacitor is added using Miller compensation. What effect does this have?",
     {'a': 'Reduces DC gain',
      'b': 'Shifts dominant pole lower',
      'c': 'Increases unity-gain bandwidth',
      'd': 'Decreases phase margin'},
     {'b'}, None),

    (44,
     "Given a two-pole system with poles at 100 Hz and 1 kHz, "
     "what compensation technique ensures stability?",
     {'a': 'Increase gain',      'b': 'Miller compensation',
      'c': 'Add zero at 1 MHz',  'd': 'Decrease DC gain'},
     {'b'}, None),

    (45,
     "A feedback amplifier has a step response with 25% overshoot. "
     "Estimate the phase margin.",
     {'a': '30\u00b0', 'b': '45\u00b0', 'c': '60\u00b0', 'd': '75\u00b0'},
     {'b'}, None),

    (46,
     "What is the primary reason for using feedback in amplifiers "
     "with respect to frequency response?",
     {'a': 'Increase gain',          'b': 'Reduce input impedance',
      'c': 'Improve linearity and stability', 'd': 'Decrease bandwidth'},
     {'c'}, None),

    (47,
     "A low phase margin usually indicates:",
     {'a': 'A more stable system',        'b': 'A faster system with no overshoot',
      'c': 'Potential for oscillation and ringing', 'd': 'Better low-frequency response'},
     {'c'}, None),

    (48,
     "Narrowbanding compensation is most effective for:",
     {'a': 'Increasing bandwidth',       'b': 'Reducing loop gain',
      'c': 'Isolating high-frequency poles', 'd': 'Preventing low-frequency oscillations'},
     {'c'}, None),

    (49,
     "Which of the following best describes Miller compensation? "
     "*(Both B and C receive full credit.)*",
     {'a': 'It increases the output resistance',
      'b': 'It adds a zero to the loop gain',
      'c': 'It creates a dominant low-frequency pole',
      'd': 'It decreases power consumption'},
     {'b', 'c'}, None),

    (50,
     "What happens to the step response of a system as phase margin increases?",
     {'a': 'Overshoot increases',   'b': 'Rise time decreases',
      'c': 'Overshoot decreases',   'd': 'System becomes underdamped'},
     {'c'}, None),

    (51,
     "Why is phase margin important in feedback amplifiers?",
     {'a': 'It determines power efficiency',
      'b': 'It directly affects the bandwidth',
      'c': 'It controls the steady-state error',
      'd': 'It predicts stability and transient response'},
     {'d'}, None),

    (52,
     "Which statement correctly distinguishes narrowbanding from Miller compensation?",
     {'a': 'Narrowbanding increases amplifier bandwidth; '
           'Miller compensation reduces high-frequency gain.',
      'b': 'Narrowbanding reduces system bandwidth to enhance selectivity; '
           'Miller compensation introduces a dominant pole to stabilize multi-stage amplifiers.',
      'c': 'Narrowbanding adds a compensating capacitor between input and output; '
           'Miller compensation adjusts biasing to reduce noise.',
      'd': 'Both techniques are exclusively used for RF amplifier impedance matching.'},
     {'b'}, None),
]

# ── QMD helpers ───────────────────────────────────────────────────────────────
KEYS = ['a', 'b', 'c', 'd']


def build_options_html(options: dict, correct: set) -> str:
    """Raw HTML ul block (via {=html} fence) so pandoc fenced-div parsing is not broken."""
    lines = ['```{=html}', '<ul class="answer-list">']
    for k in KEYS:
        if k not in options:
            continue
        text = options[k]
        if k in correct:
            lines.append(
                f'  <li class="correct-answer"><strong>{k}.</strong> {text}</li>'
            )
        else:
            lines.append(
                f'  <li class="fragment semi-fade-out" data-fragment-index="1">'
                f'{k}. {text}</li>'
            )
    lines.append('</ul>')
    lines.append('```')
    return '\n'.join(lines)


def text_slide(num: int, question: str, opts_html: str) -> str:
    return (
        '\n\n## Q' + str(num) + ' {.smaller}\n\n'
        + question + '\n\n'
        + opts_html + '\n'
    )


def figure_slide(num: int, question: str, opts_html: str, fig: str) -> str:
    alt = f"Circuit diagram for Q{num}"
    return (
        '\n\n## Q' + str(num) + ' {.smaller}\n\n'
        ':::: {.columns}\n\n'
        '::: {.column width="46%"}\n'
        '![](' + fig + '){width=100% fig-alt="' + alt + '"}\n'
        ':::\n\n'
        '::: {.column width="54%"}\n'
        + question + '\n\n'
        + opts_html + '\n'
        ':::\n\n'
        '::::\n'
    )


# ── Static content ────────────────────────────────────────────────────────────
YAML_HEADER = """\
---
format:
  revealjs:
    theme:
      - ../law.scss
    css: exam3_styles.css
    slide-number: true
    footer: "EEE 141 \u00b7 Exam #3 \u00b7 2nd Semester 2024-2025 (Set A)"
    hash: true
    controls: true
---"""

CSS_CONTENT = """\
/* exam3_styles.css — answer-reveal styling for EEE 141 Exam 3 */

/* ── Answer list ────────────────────────────────────────────── */
.answer-list {
  list-style: none;
  padding-left: 0;
  margin-top: 0.5em;
  font-size: inherit;
}

.answer-list li {
  padding: 0.15em 0.45em;
  margin: 0.22em 0;
  border-radius: 3px;
}

/* Correct answer: soft green so it pops on the dark background */
.answer-list li.correct-answer {
  color: #a8e6a3;
}

.answer-list li.correct-answer strong {
  color: #6fcf97;
}

/* Ensure opacity transitions look clean on dark bg */
.reveal .fragment.semi-fade-out.visible {
  opacity: 0.25;
}
"""

# ── Assemble QMD ─────────────────────────────────────────────────────────────
print("── Generating QMD ─────────────────────────────────────────────")
parts = [YAML_HEADER]

for num, question, options, correct, fig in QUESTIONS:
    html = build_options_html(options, correct)
    if fig:
        parts.append(figure_slide(num, question, html, fig))
    else:
        parts.append(text_slide(num, question, html))

qmd_content = '\n'.join(parts)

with open(QMD, 'w', encoding='utf-8') as f:
    f.write(qmd_content)
print(f"  Written: {QMD}")

with open(CSS, 'w', encoding='utf-8') as f:
    f.write(CSS_CONTENT)
print(f"  Written: {CSS}")
print(f"  Total slides: {len(QUESTIONS)}")
print("Done!")
