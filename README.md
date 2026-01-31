# GitHub Project Summary Generator

This tool generates summary images for GitHub repositories. It captures repository details, language statistics, and a visual preview, providing a clean banner that can be used in a profile or documentation.

## Features

- **Automated Summaries**: Fetches repository data directly from the GitHub API.
- **Visual Previews**: Integrates repository previews using `github-preview-extractor`.
- **Language Statistics**: Real-time language breakdown with accurate colors sourced from [GitHub Linguist](https://github.com/github-linguist/linguist).
- **Responsive Banners**: Generates dark-themed banners using HTML/CSS templates.
- **GitHub Actions Integration**: Automatically update your summary images on a schedule or via manual triggers.

## How It Works

1. **Data Fetching**: The script connects to the GitHub API to retrieve metadata (stars, description, visibility) and language distribution for specified repositories.
2. **Color Extraction**: It fetches the latest `languages.yml` from GitHub Linguist to ensure language colors match GitHub's native UI.
3. **Template Rendering**: Uses **Jinja2** to populate an HTML template (`src/resources/visualization.html`) with the repository data.
4. **Image Generation**: Employs **Playwright** to render the HTML in a headless browser and capture a high-resolution screenshot of the banner.

## Setup

### Prerequisites

- Python 3.11+
- [Playwright](https://playwright.dev/)
- GitHub Personal Access Token (for API access)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/nathan-roe/github-project-summary.git
   cd github-project-summary
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Or manually:
   pip install requests jinja2 playwright
   playwright install chromium
   ```

3. Install the preview extractor dependency:
   ```bash
   git clone https://github.com/nathan-roe/github-preview-extractor
   pip install -e ./github-preview-extractor
   ```

## Usage

### Local Execution

Set the required environment variables and run the generator:

```bash
export GITHUB_USER="your-username"
export GITHUB_TOKEN="your-token"
export REPOSITORIES="repo1,repo2,repo3"
export PYTHONPATH=.

python src/project_summary/generate_summary.py
```

Generated images will be saved in `src/resources/`.

### GitHub Actions

The project includes a workflow to automate image generation. You can trigger it manually via the **Actions** tab:

1. Go to your repository on GitHub.
2. Navigate to **Actions** > **Update Project Summaries**.
3. Click **Run workflow** and enter the repository names (comma-separated).

The workflow will generate the images and commit them back to your repository.

## Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|--------|
| `GITHUB_USER` | Your GitHub username. | |
| `GITHUB_TOKEN` | GitHub Personal Access Token. | |
| `REPOSITORIES` | Comma-separated list of repository names to summarize. | |
