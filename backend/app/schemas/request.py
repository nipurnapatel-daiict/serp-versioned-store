"""
Request schema models for API input validation.
Defines Pydantic models for incoming request payloads.
"""

from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """
    Search request payload schema.
    
    Attributes:
        keyword: Target keyword or keyphrase string (2-200 characters).
    """
    keyword: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Target keyword or keyphrase string passed by the client UI"
    )

    @field_validator("keyword")
    @classmethod
    def clean_keyword(cls, value: str) -> str:
        """
        Cleans user text inputs systematically.
        
        Strips whitespace and converts to lowercase. Fails early if inputs 
        are empty or contain only whitespace characters.
        
        Args:
            value: Raw input keyword string.
            
        Returns:
            Cleaned lowercase keyword string.
            
        Raises:
            ValueError: If keyword is null, empty, or whitespace only.
        """
        if not value:
            raise ValueError("Keyword string cannot be null or empty.")
            
        cleaned_value = value.strip().lower()
        
        if not cleaned_value:
            raise ValueError("Keyword cannot consist solely of blank whitespace elements.")
            
        return cleaned_value
