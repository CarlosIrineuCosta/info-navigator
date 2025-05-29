["title"]) > 200:
            card_data["title"] = card_data["title"][:197] + "..."
        
        if len(card_data["summary"]) > 300:
            card_data["summary"] = card_data["summary"][:297] + "..."
        
        if len(card_data["detailed_content"]) > 1500:
            card_data["detailed_content"] = card_data["detailed_content"][:1497] + "..."
        
        # Add content type specific enhancements
        if "domain_specific" not in card_data:
            card_data["domain_specific"] = {}
        
        # Content type specific validation and enhancement
        if content_type == ContentType.SPACE:
            card_data["domain_specific"]["content_category"] = "space_exploration"
        elif content_type == ContentType.WELLNESS:
            card_data["domain_specific"]["content_category"] = "health_wellness"
        elif content_type == ContentType.NUTRITION:
            card_data["domain_specific"]["content_category"] = "nutrition_health"
        
        return card_data
    
    def _validate_set_metadata(self, metadata: Dict[str, Any], 
                              request: ContentGenerationRequest) -> Dict[str, Any]:
        """Validate and enhance set metadata"""
        
        # Ensure required fields
        if "title" not in metadata or not metadata["title"]:
            metadata["title"] = f"Explorando {request.topic.title()}"
        
        if "description" not in metadata or not metadata["description"]:
            metadata["description"] = f"Descubra os fascinantes aspectos de {request.topic}"
        
        # Set reasonable defaults
        if "estimated_time_minutes" not in metadata:
            metadata["estimated_time_minutes"] = request.card_count * 3  # 3 min per card average
        
        # Ensure navigation suggestions are valid
        if "suggested_navigation" not in metadata:
            metadata["suggested_navigation"] = ["thematic", "random"]
        
        return metadata


class ContentGenerationError(Exception):
    """Custom exception for content generation errors"""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


# Fallback generator for when jsonformer-claude is not available
class FallbackContentGenerator:
    """Simple fallback content generator without structured validation"""
    
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Client(api_key=anthropic_api_key)
    
    async def generate_content_card(self, topic: str, content_type: ContentType, 
                                   card_context: str = "") -> Dict[str, Any]:
        """Generate content using regular Claude API with manual parsing"""
        
        prompt = f"""Create educational content about: {topic}
Content Type: {content_type.value}
Context: {card_context}

Respond in EXACTLY this format (Portuguese Brazil):

TITLE: [Engaging question, max 200 chars]
SUMMARY: [Brief answer, 2-3 sentences, max 300 chars]  
DETAILED: [Full explanation, 3-4 paragraphs, max 1500 chars]
KEYWORDS: [keyword1, keyword2, keyword3, keyword4, keyword5]
DIFFICULTY: [beginner/intermediate/advanced]

Do not include any other text or formatting."""
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the structured response
            content = response.content[0].text
            return self._parse_structured_response(content)
            
        except Exception as e:
            raise ContentGenerationError(f"Fallback generation failed: {str(e)}")
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response format"""
        import re
        
        patterns = {
            'title': r'TITLE:\s*(.+)',
            'summary': r'SUMMARY:\s*(.+?)(?=DETAILED:|$)',
            'detailed_content': r'DETAILED:\s*(.+?)(?=KEYWORDS:|$)',
            'keywords': r'KEYWORDS:\s*(.+?)(?=DIFFICULTY:|$)',
            'difficulty': r'DIFFICULTY:\s*(.+)'
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field == 'keywords':
                    # Parse comma-separated keywords
                    extracted[field] = [k.strip() for k in value.split(',')]
                elif field == 'difficulty':
                    extracted['difficulty_tags'] = [value.lower()]
                else:
                    extracted[field] = value
            else:
                # Provide defaults for missing fields
                if field == 'title':
                    extracted[field] = "Conteúdo Educativo"
                elif field == 'summary':
                    extracted[field] = "Informação educativa interessante."
                elif field == 'detailed_content':
                    extracted[field] = "Conteúdo detalhado sobre o tópico."
                elif field == 'keywords':
                    extracted[field] = ["educação", "aprendizado"]
                elif field == 'difficulty':
                    extracted['difficulty_tags'] = ["intermediate"]
        
        # Add domain_specific placeholder
        extracted['domain_specific'] = {}
        
        return extracted


# Factory function to get the appropriate generator
def get_content_generator(anthropic_api_key: str) -> Union[StructuredContentGenerator, FallbackContentGenerator]:
    """Get the best available content generator"""
    if JSONFORMER_AVAILABLE:
        return StructuredContentGenerator(anthropic_api_key)
    else:
        print("Using fallback generator - install jsonformer-claude for better reliability")
        return FallbackContentGenerator(anthropic_api_key)


if __name__ == "__main__":
    # Test the generator (requires API key)
    import os
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable to test")
    else:
        generator = get_content_generator(api_key)
        
        # Test content generation
        request = ContentGenerationRequest(
            topic="alimentos fermentados",
            content_type=ContentType.NUTRITION,
            card_count=5
        )
        
        print("Testing content generation...")
        # Note: This would require async execution in real usage
