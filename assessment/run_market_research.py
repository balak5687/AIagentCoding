#!/usr/bin/env python3
"""Market Research Agent — researches garage management products and writes to conversation.md"""
import subprocess
import sys
from pathlib import Path

CONV_FILE = Path("/home/ubuntu/bala/AIagentCoding/assessment/conversation.md")

PROMPT = """You are a market research analyst. Research the garage management software market.

Research and write a detailed analysis covering:

## Existing Commercial Products
| Product | Target Market | Key Features | Pricing | Mobile App | Tech |
|---|---|---|---|---|---|
Include: GaragePlug, Shop-Ware, Mitchell 1 Manager, Tekmetric, AutoLeap, Fullbay, Bay-master, Garage Assistant

## Open Source Alternatives
List any open source garage/auto workshop management systems on GitHub — name, stars, activity, features

## Market Gaps
What do small independent garages complain about with existing software? (slow, expensive, complex, no mobile)

## Mobile vs Web Usage
Do mechanics actually use phones/tablets on the workshop floor? What evidence exists?

## Competitor Tech Stacks
What frontend tech do market leaders use — React, Angular, native mobile, Flutter, PWA?

## Key Finding for Flutter Assessment
Based on market evidence: is a mobile-first or web-first approach more important for independent garages?

Be specific and factual. Use your knowledge of these products. Write directly to the conversation file.

After writing your analysis, output ONLY the text to replace the market research section — starting with:
## MARKET RESEARCH (COMPLETE)

End with: ---MARKET-RESEARCH-DONE---"""

print("[market-research] Starting... (2-3 min)")
sys.stdout.flush()

cmd = ["claude", "--print", "--model", "sonnet", "--dangerously-skip-permissions"]
result = subprocess.run(
    cmd, input=PROMPT, text=True,
    capture_output=True, timeout=300
)

if result.returncode != 0:
    print(f"[market-research] ERROR: {result.stderr[:200]}")
    sys.exit(1)

output = result.stdout.strip()

# Extract content between start marker and done marker
if "## MARKET RESEARCH" in output:
    start = output.find("## MARKET RESEARCH")
    end = output.find("---MARKET-RESEARCH-DONE---")
    if end > 0:
        output = output[start:end].strip()
    else:
        output = output[start:].strip()

# Write to conversation file
content = CONV_FILE.read_text()
content = content.replace(
    "## MARKET RESEARCH\n*[Pending — Market Research Agent]*",
    output
)
CONV_FILE.write_text(content)

print("[market-research] ✓ Written to conversation.md")
print(f"[market-research] {len(output)} chars")
