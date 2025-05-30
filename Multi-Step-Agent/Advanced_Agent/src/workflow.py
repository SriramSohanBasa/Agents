from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import FirecrawlService
from .prompts import DeveloperToolsPrompts 


class Workflow:
    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature = 0.1
        )
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()


    def _build_workflow(self):
            graph = StateGraph(ResearchState)

            graph.add_node("extract_tools", self._extract_tools_step)
            graph.add_node("research", self._research_step)
            graph.add_node("analyze", self._analyze_step)

            graph.set_entry_point("extract_tools")

            graph.add_edge("extract_tools", "research")
            graph.add_edge("research", "analyze")
            graph.add_edge("analyze", END)

            return graph.compile()
            



    ##build langgraph, flow the agent through and control the flow or state of agent
    """in the 1st stage, we are going to extract the various tools
    that could be candidates for what it is that we are trying to research
    
    2nd stage would be researching these obtained tools
    
    3rd step would be analysis"""

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, any]:
        print(f"Finding articles about : {state.query}")

        article_query = f"{state.query} tools comparision best alternatives" ## getting an article
        search_results = self.firecrawl.search_companies(article_query, num_results=3) ## getting a search results



        ##obtaining data from all the articles
    
        all_content = ""
        ##combine search results into single content and give to llm
        for result in search_results.data:
            url = result.get("url", "")
            scraped = self.firecrawl.scrape_company_pages(url)
            if scraped:
                all_content + scraped.markdown[:1500] + "\n\n"
            

            ##STEP-1
        ## Now passing to the LLM
            messages = [
                SystemMessage(content = self.prompts.TOOL_ANALYSIS_SYSTEM),
                HumanMessage(content = self.prompts.tool_extraction_user(state.query, all_content))
            ]
        
        try:
            response = self.llm.invoke(messages)
            tool_names = [
                name.strip()
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            print(f"Extracted tools:{',' .join(tool_names[:5])}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            print(e)
            return {"extracted tools": []}
            


    ##step-2 ANALYSIS COMPANY URL
    def _analyze_company_content(self, company_name: str, content:str) -> CompanyAnalysis: 
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)
        
        ##llm takes the content
        messages = [
            SystemMessage(content = self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content = self.prompts.tool_analysis_user(company_name, content))

        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model = "Unknown",
                is_open_source = None,
                tech_stack = [],
                description = "Failed",
                api_available= None,
                language_support=[],
                integration_capabilities=[],
            )
        




##STEP-3
    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", []) ## either give tools or give empty

        if not extracted_tools:
            print("No extracted tools found, falling back to direct search")
            search_results = self.firecrawl.search_companies(state.query, num_results=4)
            tool_names= [
                result.get("metadata", {}).get("title","Unknown")
                for result in search_results.data

            ]
        else:
            tool_names = extracted_tools[:4]
        
        print(f"Researching specific tools:{', '.join(tool_names)}")

        companies = []

        for tool_name in tool_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + "official site" ,  num_results=1)

            if tool_search_results:
                result = tool_search_results.data[0]
                url = result.get("url", "")
                    
                company = CompanyInfo(
                    name = tool_name,
                    description = result.get("markdown", ""),
                    website=url,
                    tech_stack = [],
                     competitors = []
                )


                scraped = self.firecrawl.scrape_company_pages(url)
                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content)

                    company.pricing_model=analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities 

                companies.append(company)

        return {"companies": companies}
    

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("Generating recommendations")


        company_data =", " .join([
            company.json() for company in state.companies
        ])


        messages =[
            SystemMessage(content = self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content = self.prompts.recommendations_user(state.query, company_data))
        ]


        ##passing this to llm

        response = self.llm.invoke(messages)
        return {"analysis": response.content}
    

    ##now connecting the nodes in graph. build graph method

    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query = query) ## defauly we get query and then we initialize the steps
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state) ## converting to python obj of custom class