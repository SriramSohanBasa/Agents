from typing import List, Optional, Dict, Any
from pydantic import BaseModel ##validate data easily


##models are being used telling our llm to take all of text data from web and pipe it into python objects
class CompanyAnalysis(BaseModel):
    """structured output for LLM company analysis focused on developer tools, this also acts as a schema for the llm to follow"""
    pricing_model: str ##free, freemium, paid, unknown
    is_open_source : Optional[bool] = None
    tech_stack : List[str] = []
    description: str = " "
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []



class CompanyInfo(BaseModel):
    name: str
    description: str
    website: str
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack : List[str] = []
    competitors: List[str] = []
    ##Developer specific fields
    api_available : Optional[bool] = None
    language_support = List[str] = []
    integration_capabilities : List[str] = []
    developer_experience_rating: Optional[str] = None ## we can set Poor, Good, Exxcelent


class ResearchState(BaseModel):
    query: str
    extracted_tools : List[str] = [] ## tools extracted from articls
    companies : List[CompanyInfo] =[]
    search_results : List[Dict[str, Any]] = []
    analysis : Optional[str] = None
