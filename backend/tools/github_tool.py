from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests


class GithubToolInput(BaseModel):
    github_username: str = Field(
        ...,
        description="GitHub username to analyze"
    )


class GithubRepoTool(BaseTool):
    name: str = "GitHub Repository Analyzer"
    description: str = (
        "Fetches GitHub repositories and extracts projects, "
        "languages, and repository descriptions."
    )

    args_schema: Type[BaseModel] = GithubToolInput

    def _run(self, github_username: str) -> str:
        if not github_username:
            return "No GitHub profile provided."

        url = f"https://api.github.com/users/{github_username}/repos"

        response = requests.get(url)

        if response.status_code != 200:
            return f"Failed to fetch repositories for user: {github_username}"

        repos = response.json()

        if not repos:
            return "No repositories found."

        results = []

        for repo in repos:

            repo_name = repo.get("name", "N/A")
            description = repo.get("description", "No description")
            language = repo.get("language", "Unknown")
            stars = repo.get("stargazers_count", 0)

            repo_info = f"""
Repository Name: {repo_name}
Description: {description}
Main Language: {language}
Stars: {stars}
"""

            results.append(repo_info)

        return "\n\n".join(results)