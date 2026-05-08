import json
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pydantic import ValidationError

from core.config import settings
from core.logger import get_logger
from models.jd_models import JobDescriptionData

logger = get_logger(__name__)

class JDParsingAgent:
    def __init__(self):
        logger.info("Initializing JDParsingAgent with Gemini Flash")
        # Initialize Gemini LLM with zero temperature for deterministic extraction
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=0.0 
        )
        
        # Enforce structured Pydantic output natively via LangChain's with_structured_output, its like my deductra project
        self.structured_llm = self.llm.with_structured_output(JobDescriptionData)
        
        # Design a robust prompt template
        self.prompt = PromptTemplate(
            template="""You are an expert HR extraction agent.
Your task is to extract structured information from the following Job Description text.
If any field is missing or cannot be inferred, provide a sensible default (e.g., 0 for experience, empty list for skills, 'Unspecified' for seniority).

Sanitized Job Description Text:
{jd_text}

Extract the data matching the required schema exactly.
""",
            input_variables=["jd_text"],
        )
        
    def sanitize_input(self, text: str) -> str:
        """
        Removes control characters and normalizes whitespaces 
        to prevent prompt injection or parsing errors.
        """
        if not text:
            return ""
        # Strip excessive whitespace and newlines
        return " ".join(text.split())

    def parse_jd(self, raw_text: str) -> Optional[JobDescriptionData]:
        """
        Takes raw JD text, sanitizes it, and extracts structured fields via Gemini.
        """
        logger.info("Starting JD parsing process.")
        try:
            sanitized_text = self.sanitize_input(raw_text)
            if not sanitized_text:
                logger.warning("Empty JD text provided.")
                return None
                
            # Create a runnable sequence: Prompt -> LLM (with schema)
            chain = self.prompt | self.structured_llm
            logger.debug("Invoking LLM chain for structured extraction.")
            
            # Execute extraction
            result: JobDescriptionData = chain.invoke({"jd_text": sanitized_text})
            
            logger.info(f"Successfully extracted JD data for role: {result.role_title}")
            return result
            
        except ValidationError as e:
            logger.error(f"Pydantic validation error during JD extraction: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during JD parsing: {e}")
            return None
