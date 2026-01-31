import os
import requests
import base64
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from gh_preview_extractor import extract_preview_for_repo

from src.project_summary.lang_color_extractor import get_language_color_map

user =  os.environ.get("GITHUB_USER", "")
token = os.environ.get("GITHUB_TOKEN", "")

url = f"https://api.github.com/users/{user}/repos"

headers = {
    "Accept": "application/vnd.github+json",
    **({"Authorization": f"Bearer {token}"} if token else {}),
}

repositories_to_display = os.environ.get("REPOSITORIES", "").split(",")
repositories_to_display = [r.strip() for r in repositories_to_display]

class GhRepository:
    def __init__(self, repo):
        self.name = repo.get('name')
        preview_data = extract_preview_for_repo(self.name)
        if preview_data:
            base64_preview = base64.b64encode(preview_data).decode('utf-8')
            self.preview = f"data:image/png;base64,{base64_preview}"
        else:
            self.preview = ""
        self.language_map = self.get_languages(repo)
        self.description = repo.get('description') or ""
        self.stars = repo.get('stargazers_count', 0)
        self.visibility = repo.get('visibility', 'public').capitalize()
        self.html_url = repo.get('html_url')

    @property
    def total_language_size(self):
        return sum(self.language_map.values())

    @staticmethod
    def get_languages(repo) -> dict[str, int]:
        if "languages_url" in repo:
            response = requests.get(url=repo["languages_url"], headers=headers)
            response.raise_for_status()
            languages = response.json()
            # Normalize language names for CSS variables
            return {
                lang: size for lang, size in languages.items()
            }
        return {}

    @property
    def normalized_languages(self):
        return [
            {
                "name": lang,
                "size": size,
                "css_name": lang.lower().replace(" ", "-").replace("#", "sharp").replace("+", "plus"),
                "color_var": f"var(--lang-{lang.lower().replace(' ', '-').replace('#', 'sharp').replace('+', 'plus')}, #8b949e)"
            }
            for lang, size in self.language_map.items()
        ]



if __name__ == "__main__":
    repository_res = requests.get(url=f"https://api.github.com/users/{user}/repos", headers=headers)
    repository_res.raise_for_status()
    
    repositories = [GhRepository(r) for r in repository_res.json() if r is not None and 'name' in r and r.get('name') in repositories_to_display]
    
    # Setup Jinja2 environment
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
    os.makedirs(template_dir, exist_ok=True)
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('visualization.html')
    
    # Use Playwright to take a screenshot of each repository
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1050, "height": 100})
        
        for repo in repositories:
            # Render the template for a single repository
            output_html = template.render(repositories=[repo], color_map=get_language_color_map(headers))
            
            output_image_path = os.path.join(template_dir, f'{repo.name}.png')
            
            page.set_content(output_html)
            
            # Add a small delay for any images (like the base64 previews) to render fully
            page.wait_for_timeout(1000)
            
            # Take screenshot of the banner to only capture the content
            page.locator(".repo-banner").screenshot(path=output_image_path, omit_background=True)
            print(f"Summary image generated at: {output_image_path}")

        browser.close()
