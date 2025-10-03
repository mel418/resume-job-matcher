# Resume Job Matcher

An AI-powered CLI tool that analyzes your resume against job descriptions to optimize for ATS (Applicant Tracking Systems) and increase your interview chances.

## Features

- **Match Score Analysis**: Get a 0-100 compatibility score between your resume and job posting
- **Missing Keywords Detection**: Identify the top 5 keywords you're missing from the job description
- **Actionable Improvements**: Receive 5 specific, concrete suggestions to improve your resume
- **Rewritten Examples**: See 3 before/after bullet point examples with strategic keyword placement
- **ATS Optimization Tips**: Get formatting and structure recommendations for better ATS parsing
- **JSON Export**: Save your analysis results with timestamps for tracking improvements

## Prerequisites

- Python 3.8 or higher
- An Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd resume-job-matcher
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Anthropic API key:**

   **Windows (Command Prompt):**
   ```cmd
   set ANTHROPIC_API_KEY=your_api_key_here
   ```

   **Windows (PowerShell):**
   ```powershell
   $env:ANTHROPIC_API_KEY="your_api_key_here"
   ```

   **Linux/Mac:**
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

   **For permanent setup**, add the environment variable to your system:
   - Windows: System Properties > Environment Variables
   - Linux/Mac: Add to `~/.bashrc` or `~/.zshrc`

## Usage

### Quick Start with Example Files

Run the tool with the provided example files:

```bash
python resume_matcher.py
```

When prompted:
- Resume file: `example_resume.txt`
- Job description file: `example_job.txt`

### Use with Your Own Files

1. Prepare your resume and job description as plain text files (.txt)
2. Run the script:
   ```bash
   python resume_matcher.py
   ```
3. Enter the paths to your files when prompted
4. Review the colorful analysis output
5. Optionally save results to a timestamped JSON file

## Example Output

The tool provides:

📊 **Overall Match Score** - Color-coded score with explanation

🔍 **Top 5 Missing Keywords** - Critical terms to add

💡 **5 Actionable Improvements** - Specific changes to make

✨ **Example Rewritten Bullet Points** - Before/after comparisons showing keyword integration

🎯 **ATS Optimization Tips** - Formatting and structure advice

## Output Files

If you choose to save results, a JSON file will be created with the format:
```
resume_analysis_YYYYMMDD_HHMMSS.json
```

This file contains:
- Timestamp
- File paths analyzed
- Complete analysis results
- All recommendations and examples

## Tips for Best Results

1. **Use plain text versions** of your resume and job descriptions
2. **Include complete job postings** (responsibilities, requirements, qualifications)
3. **Run multiple iterations** as you improve your resume
4. **Compare scores** across different versions to track progress
5. **Focus on relevant keywords** without keyword stuffing

## Troubleshooting

**"ANTHROPIC_API_KEY environment variable not set"**
- Make sure you've set the API key in your current terminal session
- Check for typos in the variable name
- On Windows, try restarting your terminal after setting the variable

**"File not found" error**
- Use full paths to files: `C:\Users\YourName\Documents\resume.txt`
- Or use relative paths from the current directory: `example_resume.txt`
- Check that file extensions match (.txt)

**API errors**
- Verify your API key is valid
- Check your Anthropic account has available credits
- Ensure you have internet connectivity

## License

MIT License - Feel free to modify and use for your job search!

## Contributing

Found a bug or have a feature suggestion? Feel free to open an issue or submit a pull request.
