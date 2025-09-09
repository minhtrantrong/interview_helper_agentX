"""
Bulletproof AI Integration Manager
Handles multiple models, fallbacks, caching, and cost control
"""
import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import openai
from anthropic import Anthropic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIModelConfig:
    name: str
    provider: str
    model_id: str
    cost_per_1k_tokens: float
    max_tokens: int
    priority: int  # Lower = higher priority

@dataclass 
class AnalysisResult:
    success: bool
    data: Optional[Dict]
    model_used: str
    tokens_used: int
    cost: float
    error: Optional[str] = None

class AIModelManager:
    """Manages multiple AI models with intelligent fallbacks"""
    
    def __init__(self):
        self.models = [
            AIModelConfig(
                name="Claude Sonnet 4", 
                provider="anthropic",
                model_id="claude-sonnet-4-20250514",
                cost_per_1k_tokens=0.015,
                max_tokens=4000,
                priority=1
            ),
            AIModelConfig(
                name="Claude Haiku",
                provider="anthropic", 
                model_id="claude-3-haiku-20240307",
                cost_per_1k_tokens=0.0025,
                max_tokens=4000,
                priority=2
            ),
            AIModelConfig(
                name="GPT-4o Mini",
                provider="openai",
                model_id="gpt-4o-mini",
                cost_per_1k_tokens=0.0015,
                max_tokens=4000,
                priority=3
            )
        ]
        
        # Initialize clients
        self.anthropic_client = None
        self.openai_client = None
        
        # Budget controls
        self.daily_budget = float(os.getenv("AI_DAILY_BUDGET", "10.0"))  # $10/day
        self.daily_spending = 0.0
        self.last_reset = datetime.now().date()
        
        # Simple cache for repeated queries
        self.cache = {}
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI clients with error handling"""
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key and anthropic_key != "your_anthropic_api_key_here":
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic client initialized")
        except Exception as e:
            logger.warning(f"❌ Anthropic initialization failed: {e}")
        
        try:
            openai_key = os.getenv("OPENAI_API_KEY") 
            if openai_key and openai_key != "your_openai_api_key_here":
                openai.api_key = openai_key
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.warning(f"❌ OpenAI initialization failed: {e}")
    
    def _reset_daily_budget(self):
        """Reset daily spending if it's a new day"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_spending = 0.0
            self.last_reset = today
            logger.info(f"🔄 Daily budget reset: ${self.daily_budget}")
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for prompt"""
        return hashlib.md5(prompt.encode()).hexdigest()[:16]
    
    def _check_cache(self, prompt: str) -> Optional[Dict]:
        """Check if we have cached result"""
        cache_key = self._get_cache_key(prompt)
        if cache_key in self.cache:
            logger.info("🎯 Cache hit - using cached result")
            return self.cache[cache_key]
        return None
    
    def _save_to_cache(self, prompt: str, result: Dict):
        """Save result to cache"""
        cache_key = self._get_cache_key(prompt)
        self.cache[cache_key] = result
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)"""
        return len(text) // 4
    
    def _call_anthropic(self, model_id: str, prompt: str, max_tokens: int) -> Tuple[Optional[str], int]:
        """Call Anthropic API with error handling"""
        if not self.anthropic_client:
            return None, 0
            
        try:
            response = self.anthropic_client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            return response.content[0].text, tokens_used
            
        except Exception as e:
            logger.error(f"❌ Anthropic API error: {e}")
            return None, 0
    
    def _call_openai(self, model_id: str, prompt: str, max_tokens: int) -> Tuple[Optional[str], int]:
        """Call OpenAI API with error handling"""
        if not self.openai_client:
            return None, 0
            
        try:
            response = self.openai_client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            tokens_used = response.usage.total_tokens
            return response.choices[0].message.content, tokens_used
            
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return None, 0
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from AI response with multiple strategies"""
        if not response:
            return None
            
        # Strategy 1: Find JSON block
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Try entire response
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Look for markdown code blocks
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _fallback_analysis(self, cv_text: str, job_description: str) -> Dict:
        """Rule-based fallback when AI fails"""
        logger.info("🔧 Using fallback rule-based analysis")
        
        # Simple keyword extraction for skills
        common_skills = [
            # Technical
            "Python", "JavaScript", "Java", "React", "Node.js", "SQL", "AWS", "Docker",
            "Kubernetes", "Git", "HTML", "CSS", "TypeScript", "Angular", "Vue",
            # Soft skills
            "Leadership", "Communication", "Project Management", "Problem Solving",
            "Teamwork", "Analytical", "Creative", "Adaptable",
            # Education-specific
            "ESL", "TEFL", "TESOL", "CELTA", "Curriculum Development", "Assessment",
            "Adult Education", "Teaching", "Training", "Workshop", "Pedagogy"
        ]
        
        found_skills = []
        cv_lower = cv_text.lower()
        job_lower = job_description.lower()
        
        for skill in common_skills:
            if skill.lower() in cv_lower:
                found_skills.append(skill)
        
        # Simple gap analysis
        required_skills = []
        for skill in common_skills:
            if skill.lower() in job_lower and skill not in found_skills:
                required_skills.append(skill)
        
        # Basic match score
        total_mentioned = len([s for s in common_skills if s.lower() in job_lower])
        matched = len([s for s in found_skills if s.lower() in job_lower])
        match_score = matched / max(total_mentioned, 1) if total_mentioned > 0 else 0.5
        
        return {
            "extracted_skills": found_skills,
            "extracted_experience": [{"role": "See CV", "company": "Various", "duration": "Multiple years", "key_achievements": "Various achievements"}],
            "education": [{"degree": "See CV", "field": "Various", "institution": "See CV", "year": "Various"}],
            "skill_gaps": [
                {
                    "missing_skill": skill,
                    "importance": "important",
                    "suggested_resources": [f"Study {skill}", f"Practice {skill}"]
                } for skill in required_skills[:5]
            ],
            "experience_gaps": ["Review CV for specific experience gaps"],
            "match_score": round(match_score, 2),
            "recommendations": [
                "Review extracted skills for accuracy",
                "Focus on highlighted skill gaps", 
                "Consider additional qualifications",
                "Highlight relevant experience clearly"
            ]
        }
    
    def analyze_cv(self, cv_text: str, job_description: str) -> AnalysisResult:
        """Main analysis method with fallbacks"""
        self._reset_daily_budget()
        
        # Check cache first
        prompt = self._create_analysis_prompt(cv_text, job_description)
        cached_result = self._check_cache(prompt)
        if cached_result:
            return AnalysisResult(
                success=True,
                data=cached_result,
                model_used="cache",
                tokens_used=0,
                cost=0.0
            )
        
        # Check budget
        if self.daily_spending >= self.daily_budget:
            logger.warning(f"💰 Daily budget exceeded: ${self.daily_spending:.2f}")
            fallback_data = self._fallback_analysis(cv_text, job_description)
            return AnalysisResult(
                success=True,
                data=fallback_data,
                model_used="fallback_rule_based",
                tokens_used=0,
                cost=0.0
            )
        
        # Try each model in priority order
        for model in sorted(self.models, key=lambda x: x.priority):
            logger.info(f"🤖 Trying {model.name}...")
            
            # Check if we have budget for this model
            estimated_tokens = self._estimate_tokens(prompt)
            estimated_cost = (estimated_tokens / 1000) * model.cost_per_1k_tokens
            
            if self.daily_spending + estimated_cost > self.daily_budget:
                logger.warning(f"💰 Skipping {model.name} - would exceed budget")
                continue
            
            # Try the model
            response_text = None
            tokens_used = 0
            
            if model.provider == "anthropic":
                response_text, tokens_used = self._call_anthropic(model.model_id, prompt, model.max_tokens)
            elif model.provider == "openai":
                response_text, tokens_used = self._call_openai(model.model_id, prompt, model.max_tokens)
            
            if response_text:
                # Parse the response
                parsed_data = self._parse_json_response(response_text)
                
                if parsed_data:
                    # Success! Calculate cost and save
                    actual_cost = (tokens_used / 1000) * model.cost_per_1k_tokens
                    self.daily_spending += actual_cost
                    
                    # Cache the result
                    self._save_to_cache(prompt, parsed_data)
                    
                    logger.info(f"✅ Success with {model.name} - Cost: ${actual_cost:.4f}")
                    
                    return AnalysisResult(
                        success=True,
                        data=parsed_data,
                        model_used=model.name,
                        tokens_used=tokens_used,
                        cost=actual_cost
                    )
                else:
                    logger.warning(f"⚠️  {model.name} returned unparseable response")
            else:
                logger.warning(f"❌ {model.name} failed to respond")
        
        # All models failed - use fallback
        logger.info("🔧 All AI models failed, using rule-based fallback")
        fallback_data = self._fallback_analysis(cv_text, job_description)
        
        return AnalysisResult(
            success=True,
            data=fallback_data,
            model_used="fallback_rule_based", 
            tokens_used=0,
            cost=0.0
        )
    
    def _create_analysis_prompt(self, cv_text: str, job_description: str) -> str:
        """Create the analysis prompt for AI models"""
        return f"""
Please analyze the following CV against the job description and provide a structured analysis.

CV CONTENT:
{cv_text}

JOB DESCRIPTION:
{job_description}

Please provide your analysis in the following JSON format only:
{{
    "extracted_skills": ["skill1", "skill2", "skill3"],
    "extracted_experience": [
        {{"role": "Job Title", "company": "Company", "duration": "2020-2023", "key_achievements": "Key accomplishments"}}
    ],
    "education": [
        {{"degree": "Bachelor's", "field": "Computer Science", "institution": "University", "year": "2020"}}
    ],
    "skill_gaps": [
        {{
            "missing_skill": "Required Skill",
            "importance": "critical|important|nice-to-have",
            "suggested_resources": ["Resource 1", "Resource 2"]
        }}
    ],
    "experience_gaps": ["Gap 1", "Gap 2"],
    "match_score": 0.75,
    "recommendations": ["Recommendation 1", "Recommendation 2"]
}}

Return only valid JSON. Match score should be between 0.0 and 1.0.
"""
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            "daily_budget": self.daily_budget,
            "daily_spending": self.daily_spending,
            "remaining_budget": self.daily_budget - self.daily_spending,
            "cache_size": len(self.cache),
            "available_models": [m.name for m in self.models if 
                               (m.provider == "anthropic" and self.anthropic_client) or
                               (m.provider == "openai" and self.openai_client)]
        }