#!/usr/bin/env python3
"""Run a single persona agent. Called by tmux panes."""
import subprocess
import sys
import time
from pathlib import Path

PERSONAS = {
    "pm": {
        "model": "sonnet",
        "name": "Product Manager",
        "section_r1": "### Product Manager\n*[Pending]*",
        "section_r2": "### Product Manager responds\n*[Pending]*",
        "prompt_r1": """You are a Product Manager with 10 years experience in B2B SaaS for SMEs.
You are assessing whether Flutter Web is the right technology choice for GarageHQ — a garage management platform.

First read the market research in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

Then give your Round 1 opening position on:
1. Does Flutter Web align with GarageHQ's go-to-market strategy?
2. What does the market evidence tell us about mobile vs web in this sector?
3. Time-to-market implications of Flutter vs alternatives
4. Competitive positioning — does the tech choice matter to customers?
5. Your recommendation with clear reasoning

Be direct. Use data from the market research. Speak as a PM who has shipped products.
Write conversationally — this is a live debate, not a report.
Keep it under 400 words. Make strong points.""",
        "prompt_r2": """You are the Product Manager in a technology assessment debate.
Read the full conversation so far in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

Now respond to what the Technical Architect and Customer said in Round 1.
- Do you agree or disagree with the Architect's technical position?
- Does the Customer's feedback change your view?
- What's your strongest counter-argument?
Keep it punchy — under 300 words."""
    },

    "architect": {
        "model": "sonnet",
        "name": "Technical Architect",
        "section_r1": "### Technical Architect\n*[Pending]*",
        "section_r2": "### Technical Architect responds\n*[Pending]*",
        "prompt_r1": """You are a Senior Technical Architect who has built SaaS products at scale.
You are assessing whether Flutter Web is the right technology choice for GarageHQ.

First read the market research in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

Give your Round 1 technical assessment:
1. Flutter Web — real-world performance, bundle size, rendering (CanvasKit vs HTML), SEO, accessibility
2. Developer experience: build times, debugging, tooling vs React/Next.js/Vue
3. Single codebase mobile+web — is the promise real or a trap?
4. Long-term maintainability — Flutter version upgrades, breaking changes, community size
5. AI-assisted development — which stack do AI coding agents (Claude, Copilot) write better code for?
6. Your recommendation with clear reasoning

Be technically honest. Don't sugarcoat Flutter's weaknesses. Don't dismiss them either.
Write conversationally — under 400 words.""",
        "prompt_r2": """You are the Technical Architect in a technology assessment debate.
Read the full conversation in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

Respond to the PM and Customer positions:
- Where does the PM's business view conflict with technical reality?
- Does the Customer's mobile use case change your recommendation?
- What's the one technical fact that should settle this debate?
Under 300 words."""
    },

    "customer": {
        "model": "sonnet",
        "name": "Customer (Garage Owner)",
        "section_r1": "### Customer (Garage Owner)\n*[Pending]*",
        "section_r2": "### Customer responds\n*[Pending]*",
        "prompt_r1": """You are a garage owner who runs a 4-bay independent workshop with 3 mechanics.
You are evaluating GarageHQ as a replacement for your current paper-based system.
You are NOT a tech person. You care about: does it work on my phone? is it fast? can my mechanics use it?

Read the market research in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

Give your honest Round 1 reaction:
1. Do you use a tablet or phone on the workshop floor? What for?
2. What do you hate about current tools you've tried?
3. What would make you switch from paper to digital?
4. Does it matter to you what technology it's built with?
5. What would you pay for a tool that actually worked?

Speak as a real garage owner — blunt, practical, no jargon.
Under 300 words.""",
        "prompt_r2": """You are the garage owner in a technology debate.
Read the full conversation in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

The tech people are debating Flutter vs React. Respond honestly:
- Do you care about this debate?
- What did the PM or Architect say that resonated or missed the point entirely?
- What's the one thing that would make or break this product for you?
Under 200 words. Keep it real."""
    },

    "devils_advocate": {
        "model": "opus",
        "name": "Devil's Advocate",
        "section_r1": None,
        "section_r2": None,
        "prompt_r1": None,
        "prompt_r2": """You are a sharp, experienced technology investor and devil's advocate.
You have read the full debate in /home/ubuntu/bala/AIagentCoding/assessment/conversation.md

Your job: challenge every assumption, find the strongest counter-arguments, and force a real conclusion.

Structure your response as:

## DEVIL'S ADVOCATE — Final Challenge

### Challenging the PM
[What's weak in the PM's argument? What did they miss?]

### Challenging the Architect
[What's the flaw in the technical reasoning? What assumptions are wrong?]

### Challenging the Customer
[Is this customer representative? What about the other 80% of garages?]

### The Real Question Nobody Asked
[What's the actual question that should have been debated?]

### Verdict
[Forced choice — Flutter Web: keep it, replace it, or hybrid approach?
Give a definitive recommendation with your single strongest reason.
No hedging. One clear answer.]

Be brutal but fair. Maximum 500 words."""
    }
}

CONV_FILE = Path("/home/ubuntu/bala/AIagentCoding/assessment/conversation.md")


def wait_for_section(section_text: str, timeout: int = 600) -> bool:
    """Wait until a pending marker is replaced with real content."""
    start = time.time()
    while time.time() - start < timeout:
        content = CONV_FILE.read_text()
        if section_text not in content:
            return True  # Section has been filled in
        print(f"  [{time.strftime('%H:%M:%S')}] waiting for section to fill...")
        sys.stdout.flush()
        time.sleep(8)
    print(f"  TIMEOUT waiting for: {section_text[:60]}")
    return False


def update_conversation(old_text: str, new_content: str) -> None:
    content = CONV_FILE.read_text()
    content = content.replace(old_text, new_content)
    CONV_FILE.write_text(content)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in PERSONAS:
        print(f"Usage: python3 run_persona.py <{'|'.join(PERSONAS)}>")
        sys.exit(1)

    persona_key = sys.argv[1]
    p = PERSONAS[persona_key]
    print(f"\n[{p['name']}] Starting...")

    # ── ROUND 1 ──────────────────────────────────────────────────────────
    if persona_key != "devils_advocate":
        # Wait for market research to complete
        print(f"[{p['name']}] Waiting for market research...")
        wait_for_section("*[Pending — Market Research Agent]*", timeout=360)

        print(f"[{p['name']}] Writing Round 1 position...")
        context = CONV_FILE.read_text()
        full_prompt = p["prompt_r1"] + f"\n\nCurrent conversation:\n\n{context}"

        cmd = ["claude", "--print", f"--model", p["model"], "--dangerously-skip-permissions"]
        result = subprocess.run(cmd, input=full_prompt, text=True,
                               capture_output=True, timeout=300)

        r1_output = result.stdout.strip()
        r1_section = f"### {p['name']}\n\n{r1_output}\n"
        update_conversation(p["section_r1"], r1_section)
        print(f"[{p['name']}] Round 1 written ✓")

    # ── ROUND 2 ──────────────────────────────────────────────────────────
    # Wait for all Round 1s to complete
    print(f"[{p['name']}] Waiting for all Round 1 positions...")
    for other_key, other_p in PERSONAS.items():
        if other_key in ("devils_advocate", persona_key):
            continue
        if other_p["section_r1"]:
            wait_for_section(other_p["section_r1"], timeout=600)

    print(f"[{p['name']}] Writing Round 2 response...")
    context = CONV_FILE.read_text()
    full_prompt = p["prompt_r2"] + f"\n\nFull conversation so far:\n\n{context}"

    cmd = ["claude", "--print", f"--model", p["model"], "--dangerously-skip-permissions"]
    result = subprocess.run(cmd, input=full_prompt, text=True,
                           capture_output=True, timeout=300)

    r2_output = result.stdout.strip()

    if persona_key == "devils_advocate":
        da_section = f"## DEVIL'S ADVOCATE — Final Challenge\n\n{r2_output}\n"
        update_conversation("## DEVIL'S ADVOCATE — Final Challenge\n*[Pending — Opus]*", da_section)
        # Write synthesis
        synthesis = f"\n## SYNTHESIS & VERDICT\n\n*See Devil's Advocate section above for final verdict.*\n"
        update_conversation("## SYNTHESIS & VERDICT\n*[Pending]*", synthesis)
    else:
        r2_section = f"{p['section_r2'].split(chr(10))[0]}\n\n{r2_output}\n"
        update_conversation(p["section_r2"], r2_section)

    print(f"[{p['name']}] Round 2 written ✓")
    print(f"[{p['name']}] DONE")
