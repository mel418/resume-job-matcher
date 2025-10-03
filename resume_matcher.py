#!/usr/bin/env python3
"""
Resume Job Matcher - An ATS optimization tool powered by Claude AI
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

console = Console()


def read_file(file_path: str) -> str:
    """Read and return the contents of a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        console.print(f"[bold red]❌ Error: File not found: {file_path}[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Error reading file {file_path}: {str(e)}[/bold red]")
        sys.exit(1)


def get_api_key() -> str:
    """Retrieve the Anthropic API key from environment variables."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        console.print("[bold red]❌ Error: ANTHROPIC_API_KEY environment variable not set[/bold red]")
        console.print("[yellow]Please set your API key:[/yellow]")
        console.print("  Windows: set ANTHROPIC_API_KEY=your_key_here")
        console.print("  Linux/Mac: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)
    return api_key


def analyze_resume_match(resume_text: str, job_text: str, api_key: str) -> dict:
    """Use Claude API to analyze resume-job match."""

    prompt = f"""You are an expert ATS (Applicant Tracking System) optimization specialist and resume consultant. Analyze the following resume against the job description and provide detailed, actionable feedback.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_text}

Provide your analysis in the following JSON format:
{{
  "match_score": <number between 0-100>,
  "score_explanation": "<2-3 sentence explanation of the score>",
  "missing_keywords": [
    "<keyword 1>",
    "<keyword 2>",
    "<keyword 3>",
    "<keyword 4>",
    "<keyword 5>"
  ],
  "improvements": [
    "<specific actionable improvement 1>",
    "<specific actionable improvement 2>",
    "<specific actionable improvement 3>",
    "<specific actionable improvement 4>",
    "<specific actionable improvement 5>"
  ],
  "rewritten_bullets": [
    {{
      "original": "<original bullet point from resume or generic example>",
      "improved": "<rewritten version with missing keywords and ATS optimization>",
      "keywords_added": ["<keyword 1>", "<keyword 2>"]
    }},
    {{
      "original": "<original bullet point from resume or generic example>",
      "improved": "<rewritten version with missing keywords and ATS optimization>",
      "keywords_added": ["<keyword 1>", "<keyword 2>"]
    }},
    {{
      "original": "<original bullet point from resume or generic example>",
      "improved": "<rewritten version with missing keywords and ATS optimization>",
      "keywords_added": ["<keyword 1>", "<keyword 2>"]
    }}
  ],
  "ats_tips": [
    "<specific ATS formatting tip 1>",
    "<specific ATS formatting tip 2>",
    "<specific ATS formatting tip 3>"
  ]
}}

Focus on:
1. Exact keyword matching between job description and resume
2. Skills alignment (hard skills and soft skills)
3. Experience relevance and impact quantification
4. ATS-friendly formatting recommendations
5. Strategic keyword placement (not keyword stuffing)
6. Action verb usage and measurable achievements

Return ONLY the JSON object, no additional text."""

    try:
        client = Anthropic(api_key=api_key)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="🤖 Analyzing resume with Claude AI...", total=None)

            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

        response_text = message.content[0].text

        # Remove markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith('```'):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove trailing ```
        response_text = response_text.strip()

        # Parse JSON response
        result = json.loads(response_text)
        return result

    except json.JSONDecodeError as e:
        console.print(f"[bold red]❌ Error parsing API response: {str(e)}[/bold red]")
        console.print(f"[dim]Response: {response_text[:500]}...[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ API Error: {str(e)}[/bold red]")
        sys.exit(1)


def display_results(results: dict):
    """Display the analysis results in a formatted, colorful way."""

    # Match Score
    score = results['match_score']
    if score >= 80:
        score_color = "green"
        emoji = "🎉"
    elif score >= 60:
        score_color = "yellow"
        emoji = "👍"
    else:
        score_color = "red"
        emoji = "⚠️"

    console.print()
    console.print(Panel(
        f"[bold {score_color}]{emoji} Match Score: {score}/100[/bold {score_color}]\n\n{results['score_explanation']}",
        title="📊 Overall Match Score",
        border_style=score_color
    ))
    console.print()

    # Missing Keywords
    console.print(Panel(
        "\n".join([f"  • [bold cyan]{kw}[/bold cyan]" for kw in results['missing_keywords']]),
        title="🔍 Top 5 Missing Keywords",
        border_style="cyan"
    ))
    console.print()

    # Improvements
    improvements_text = "\n\n".join([
        f"[bold yellow]{i+1}.[/bold yellow] {imp}"
        for i, imp in enumerate(results['improvements'])
    ])
    console.print(Panel(
        improvements_text,
        title="💡 5 Actionable Improvements",
        border_style="yellow"
    ))
    console.print()

    # Rewritten Bullets
    bullets_text = ""
    for i, bullet in enumerate(results['rewritten_bullets'], 1):
        bullets_text += f"[bold magenta]Example {i}:[/bold magenta]\n\n"
        bullets_text += f"[dim]Before:[/dim] {bullet['original']}\n\n"
        bullets_text += f"[green]After:[/green] {bullet['improved']}\n\n"
        bullets_text += f"[cyan]Keywords added:[/cyan] {', '.join(bullet['keywords_added'])}\n"
        if i < len(results['rewritten_bullets']):
            bullets_text += "\n" + "─" * 80 + "\n\n"

    console.print(Panel(
        bullets_text,
        title="✨ Example Rewritten Bullet Points",
        border_style="magenta"
    ))
    console.print()

    # ATS Tips
    if 'ats_tips' in results:
        tips_text = "\n\n".join([
            f"  • {tip}"
            for tip in results['ats_tips']
        ])
        console.print(Panel(
            tips_text,
            title="🎯 ATS Optimization Tips",
            border_style="blue"
        ))
        console.print()


def save_results(results: dict, resume_path: str, job_path: str) -> str:
    """Save results to a timestamped JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"resume_analysis_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "resume_file": resume_path,
        "job_file": job_path,
        "analysis": results
    }

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        return output_file
    except Exception as e:
        console.print(f"[bold red]❌ Error saving results: {str(e)}[/bold red]")
        return None


def main():
    """Main CLI interface."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Resume Job Matcher[/bold cyan]\n[dim]ATS Optimization powered by Claude AI[/dim]",
        border_style="cyan"
    ))
    console.print()

    # Get file paths from user
    resume_path = console.input("[bold]📄 Enter path to resume file: [/bold]").strip()
    job_path = console.input("[bold]💼 Enter path to job description file: [/bold]").strip()

    console.print()

    # Read files
    resume_text = read_file(resume_path)
    job_text = read_file(job_path)

    console.print(f"[green]✓[/green] Resume loaded ([dim]{len(resume_text)} characters[/dim])")
    console.print(f"[green]✓[/green] Job description loaded ([dim]{len(job_text)} characters[/dim])")
    console.print()

    # Get API key
    api_key = get_api_key()

    # Analyze
    results = analyze_resume_match(resume_text, job_text, api_key)

    # Display results
    display_results(results)

    # Ask to save
    save_choice = console.input("[bold]💾 Save results to JSON file? (y/n): [/bold]").strip().lower()
    if save_choice == 'y':
        output_file = save_results(results, resume_path, job_path)
        if output_file:
            console.print(f"[green]✓ Results saved to {output_file}[/green]")

    console.print()
    console.print("[bold green]✨ Analysis complete![/bold green]")
    console.print()


if __name__ == "__main__":
    main()
