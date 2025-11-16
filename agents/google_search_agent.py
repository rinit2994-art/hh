"""Google Search Agent - Performs web searches and gathers information."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search


# Create the Google Search agent with built-in google_search tool
google_search_agent = LlmAgent(
    name="google_search_agent",
    model="gemini-2.0-flash-exp",
    description="I search the web using Google Search to find information, news, trends, and research topics.",
    instruction="""You are a web search specialist. Your role is to:

    1. Search the web for relevant information
    2. Find news and current events
    3. Research companies, stocks, and market trends
    4. Discover investment insights and financial news
    5. Validate information from multiple sources

    When searching:
    - Use specific and relevant search queries
    - Summarize key findings from search results
    - Cite sources when providing information
    - Look for recent and authoritative sources
    - Cross-reference information when accuracy is critical

    Always provide context with your search results and highlight the most relevant information.
    """,
    tools=[google_search]
)
