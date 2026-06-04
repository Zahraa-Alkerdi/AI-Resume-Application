from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from tools.github_tool import GithubRepoTool
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    return LLM(
        model=os.getenv("MODEL", "groq/llama-3.3-70b-versatile"),
        api_key=os.getenv("GROQ_API_KEY"),
        request_timeout=120,
        max_retries=3,
        temperature=0
    )


llm = get_llm()


@CrewBase
class MyCrewai():
    """MyCrewai crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # ---------------- AGENTS ----------------
    @agent
    def Analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['Analyzer'],
            llm=llm,
            verbose=True
        )

    @agent
    def Github_Analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['Github_Analyzer'],
            llm=llm,
            tools=[GithubRepoTool()],
            verbose=True
        )

    @agent
    def Editor(self) -> Agent:
        return Agent(
            config=self.agents_config['Editor'],
            llm=llm,
            verbose=True
        )

    @agent
    def ATS_and_Formatting_Specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['ATS_and_Formatting_Specialist'],
            llm=llm,
            verbose=True
        )

    @agent
    def Reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['Reviewer'],
            llm=llm,
            verbose=True
        )

    # ---------------- TASKS ----------------
    @task
    def analyzing_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyzing_task'],
            name="analysis"
        )

    @task
    def github_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['github_analysis_task'],
            name="github_analysis"
        )

    @task
    def editing_task(self) -> Task:
        return Task(
            config=self.tasks_config['editing_task'],
            name="editing"
        )

    @task
    def ats_optimization_task(self) -> Task:
        return Task(
            config=self.tasks_config['ats_optimization_task'],
            name="ats_optimization"
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            name="review"
        )

    # ---------------- CREW ----------------
    @crew
    def crew(self) -> Crew:

        analysis = self.analyzing_task()
        editing = self.editing_task()
        ats = self.ats_optimization_task()
        review = self.review_task()

        tasks = [analysis]

        if getattr(self, "has_github", False):
            tasks.append(self.github_analysis_task())

        tasks += [editing, ats, review]

        return Crew(
            agents=self.agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )