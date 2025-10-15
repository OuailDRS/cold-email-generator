import os
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from dotenv import load_dotenv
load_dotenv()

class JobInfo(BaseModel): 
    role : Optional[str] = Field(..., description="The job title or position")
    experience : Optional[str] = Field(..., description="Required experience level or years")
    skills : Optional[List[str]] = Field(..., description="List of required skills or technologies")
    description : Optional[str] = Field(..., description="Concise summary of the job description")
    
class Chain : 
    def __init__(self) : 
        self.llm =  ChatGroq(
        temperature = 0.7, 
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name = "llama-3.3-70b-versatile"
                    )   
    def extract_jobs_description(self, link) : 
        loader = WebBaseLoader(link)
        page_data = loader.load().pop().page_content
        parser = JsonOutputParser(pydantic_object=JobInfo)
        job_parser_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a job data extraction specialist. Extract information from job postings into JSON with this exact structure:
            \n {format_instructions}
            Output ONLY valid JSON, no other text."""),

                ("user", "Extract job information from this content: {scraped_content}")
            ]).partial(format_instructions=parser.get_format_instructions())
        extract_chain = job_parser_prompt | self.llm | parser 
        res = extract_chain.invoke(input = {"scraped_content":page_data})
        return res if isinstance(res,list) else [res]
    
    def write_email(self,job_description , portfolio_infos,agency_name = "Tech Talent Inc" , representative_name = "John Smith" , email_language = "English" ) : 
        cold_email_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a specialized email copywriter for the employment agency "{agency_name}". Your task is to generate a single, ready-to-send cold email based on the provided data.

        You will receive:
        1. Job opportunity in this JSON format: {{'role': '', 'experience': '', 'skills': [], 'description': ''}}
        2. Portfolio information in this JSON format: {{"skills": [], "portfolio": "link"}}

        Follow these guidelines:
        - **Tone & Format:** Write in a professional, persuasive, and slightly conversational tone. Format the output as a complete email with Subject, Body, and Signature, using plain text only (no markdown).
        - **Email Structure:** Use a proven effective structure:
            1. **Personalized Opening:** Address the hiring manager directly and create a strong hook.
            2. **Introduce the Candidate:** Present the candidate's profile, seamlessly integrating the specific skills, experience, and project details.
        3. **Portfolio Integration:** 
               - Prioritize portfolio links that directly match skills mentioned in the job description
               - You can also highlight relevant skills and portfolio links that are related to the job description but not explicitly mentioned, if they add value
        4. **Value Proposition:** Clearly state how the candidate's background aligns with the hiring manager's needs.
            5. **Call to Action:** End with a clear request to schedule a call or meeting.
        - **Output:** Generate ONLY the final email text with no preamble, explanations, or additional text.

            """), 
            ("user","""
            Agency Name: {agency_name}
            Our Representative: {representative_name}
            Email Language: {email_language}

            Job Opportunity Details (JSON):
            {job_json}

            Relevant Candidate Project Portfolio Information (JSON):
            {portfolio_info}

            Generate the cold email.

            """)
        ])
        email_chain = cold_email_prompt | self.llm 
        cold_email = email_chain.invoke({
            "agency_name": agency_name,
            "representative_name": representative_name, 
            "email_language": email_language,
            "job_json": job_description,
            "portfolio_info": portfolio_infos
        })
        return cold_email.content
        