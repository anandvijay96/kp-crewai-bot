"""
ContentAnalysisTool - Advanced content analysis and insight extraction

This tool provides:
- Content structure analysis
- Keyword and topic extraction
- Readability and engagement metrics
- SEO content optimization insights
- Integration with CrewAI for intelligent content processing
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
from textstat import flesch_reading_ease, flesch_kincaid_grade
from crewai.tools import BaseTool
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

# Module-level constants to avoid Pydantic issues
STOP_WORDS = set(stopwords.words('english'))
SEO_KEYWORDS = {
    'seo', 'search', 'optimization', 'ranking', 'traffic', 'keywords',
    'backlinks', 'content', 'marketing', 'digital', 'strategy', 'analytics',
    'conversion', 'engagement', 'social', 'organic', 'serp', 'algorithm'
}


class ContentAnalysisTool(BaseTool):
    """
    CrewAI tool for comprehensive content analysis
    
    Capabilities:
    - Text structure and readability analysis
    - Keyword density and topic extraction
    - Sentiment and engagement indicators
    - SEO optimization recommendations
    """
    
    name: str = "content_analysis_tool"
    description: str = """
    Analyze blog content to extract insights for comment generation and SEO optimization.
    
    This tool can:
    - Extract key topics and themes
    - Analyze content structure and readability
    - Identify engagement opportunities
    - Calculate keyword density and SEO metrics
    - Provide content optimization recommendations
    
    Input: Blog content text (string)
    Output: Comprehensive analysis dictionary with metrics and insights
    """
    
    def __init__(self):
        super().__init__()
        # Use module-level constants to avoid Pydantic issues
    
    def _run(self, content: str) -> Dict[str, Any]:
        """
        Main execution method for content analysis
        
        Args:
            content: The blog content to analyze
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        try:
            # Basic text metrics
            basic_metrics = self._calculate_basic_metrics(content)
            
            # Readability analysis
            readability = self._analyze_readability(content)
            
            # Keyword and topic extraction
            keywords_topics = self._extract_keywords_and_topics(content)
            
            # Content structure analysis
            structure = self._analyze_structure(content)
            
            # Engagement indicators
            engagement = self._analyze_engagement_indicators(content)
            
            # SEO relevance scoring
            seo_relevance = self._calculate_seo_relevance(content, keywords_topics['keywords'])
            
            # Comment opportunities
            comment_opportunities = self._identify_comment_opportunities(content, structure)
            
            return {
                'success': True,
                'basic_metrics': basic_metrics,
                'readability': readability,
                'keywords_topics': keywords_topics,
                'structure': structure,
                'engagement': engagement,
                'seo_relevance': seo_relevance,
                'comment_opportunities': comment_opportunities,
                'overall_score': self._calculate_overall_score(
                    basic_metrics, readability, engagement, seo_relevance
                )
            }
            
        except Exception as e:
            logging.error(f"Content analysis failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'basic_metrics': {},
                'readability': {},
                'keywords_topics': {},
                'structure': {},
                'engagement': {},
                'seo_relevance': 0,
                'comment_opportunities': [],
                'overall_score': 0
            }
    
    def _calculate_basic_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate basic text metrics"""
        sentences = sent_tokenize(content)
        words = word_tokenize(content.lower())
        
        # Filter out punctuation and stop words for meaningful word count
        meaningful_words = [
            word for word in words 
            if word.isalpha() and word not in STOP_WORDS
        ]
        
        return {
            'character_count': len(content),
            'word_count': len(words),
            'meaningful_word_count': len(meaningful_words),
            'sentence_count': len(sentences),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'avg_chars_per_word': sum(len(word) for word in meaningful_words) / len(meaningful_words) if meaningful_words else 0
        }
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        try:
            flesch_ease = flesch_reading_ease(content)
            flesch_grade = flesch_kincaid_grade(content)
            
            # Determine readability level
            if flesch_ease >= 90:
                level = "Very Easy"
            elif flesch_ease >= 80:
                level = "Easy"
            elif flesch_ease >= 70:
                level = "Fairly Easy"
            elif flesch_ease >= 60:
                level = "Standard"
            elif flesch_ease >= 50:
                level = "Fairly Difficult"
            elif flesch_ease >= 30:
                level = "Difficult"
            else:
                level = "Very Difficult"
            
            return {
                'flesch_reading_ease': flesch_ease,
                'flesch_kincaid_grade': flesch_grade,
                'readability_level': level,
                'is_accessible': flesch_ease >= 60  # Standard or easier
            }
            
        except Exception as e:
            logging.warning(f"Readability analysis failed: {e}")
            return {
                'flesch_reading_ease': 0,
                'flesch_kincaid_grade': 0,
                'readability_level': "Unknown",
                'is_accessible': False
            }
    
    def _extract_keywords_and_topics(self, content: str) -> Dict[str, Any]:
        """Extract keywords and identify main topics"""
        words = word_tokenize(content.lower())
        
        # Filter meaningful words
        meaningful_words = [
            word for word in words 
            if word.isalpha() and len(word) > 3 and word not in STOP_WORDS
        ]
        
        # Get word frequency
        word_freq = Counter(meaningful_words)
        
        # Extract top keywords
        top_keywords = [
            {'word': word, 'frequency': freq, 'density': freq/len(meaningful_words)}
            for word, freq in word_freq.most_common(20)
        ]
        
        # Identify potential topics using POS tagging
        tagged_words = pos_tag(meaningful_words)
        nouns = [word for word, pos in tagged_words if pos in ['NN', 'NNS', 'NNP', 'NNPS']]
        noun_freq = Counter(nouns)
        
        topics = [
            {'topic': topic, 'frequency': freq}
            for topic, freq in noun_freq.most_common(10)
        ]
        
        # Identify key phrases (simple bigrams and trigrams)
        phrases = self._extract_phrases(content)
        
        return {
            'keywords': top_keywords,
            'topics': topics,
            'phrases': phrases,
            'total_unique_words': len(set(meaningful_words))
        }
    
    def _extract_phrases(self, content: str) -> List[Dict[str, Any]]:
        """Extract meaningful phrases from content"""
        # Simple phrase extraction using common patterns
        phrases = []
        
        # Find phrases with common patterns
        phrase_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Proper noun phrases
            r'\b(?:digital|content|search|social) \w+\b',  # Marketing terms
            r'\b\w+ (?:strategy|optimization|marketing|analysis)\b',  # Business terms
        ]
        
        for pattern in phrase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            phrase_freq = Counter([match.lower() for match in matches])
            
            for phrase, freq in phrase_freq.most_common(5):
                if freq > 1:  # Only include phrases that appear multiple times
                    phrases.append({
                        'phrase': phrase,
                        'frequency': freq
                    })
        
        return phrases[:10]  # Return top 10 phrases
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        lines = content.split('\n')
        
        # Identify headers (simple heuristic)
        headers = []
        for i, line in enumerate(lines):
            line = line.strip()
            if line and (
                line.isupper() or 
                (len(line.split()) <= 10 and line.endswith(':')) or
                re.match(r'^#{1,6}\s', line)  # Markdown headers
            ):
                headers.append({
                    'text': line,
                    'position': i,
                    'level': self._determine_header_level(line)
                })
        
        # Identify lists
        list_items = len([line for line in lines if re.match(r'^\s*[-*•]\s', line.strip())])
        numbered_items = len([line for line in lines if re.match(r'^\s*\d+\.\s', line.strip())])
        
        # Identify questions
        questions = re.findall(r'[.!?]*\?', content)
        
        return {
            'headers': headers,
            'header_count': len(headers),
            'list_items': list_items,
            'numbered_items': numbered_items,
            'question_count': len(questions),
            'has_structured_content': len(headers) > 0 or list_items > 0 or numbered_items > 0
        }
    
    def _determine_header_level(self, header: str) -> int:
        """Determine header level based on formatting"""
        if header.startswith('#'):
            return min(6, header.count('#'))
        elif header.isupper():
            return 1
        elif header.endswith(':'):
            return 2
        else:
            return 3
    
    def _analyze_engagement_indicators(self, content: str) -> Dict[str, Any]:
        """Analyze indicators of engaging content"""
        
        # Question indicators
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        question_count = sum(content.lower().count(word + ' ') for word in question_words)
        direct_questions = len(re.findall(r'\?', content))
        
        # Action words
        action_words = [
            'discover', 'learn', 'explore', 'find', 'get', 'start', 'begin',
            'improve', 'increase', 'boost', 'optimize', 'enhance', 'achieve'
        ]
        action_count = sum(content.lower().count(word) for word in action_words)
        
        # Emotional indicators
        emotional_words = [
            'amazing', 'incredible', 'fantastic', 'excellent', 'outstanding',
            'challenging', 'difficult', 'frustrating', 'exciting', 'surprising'
        ]
        emotional_count = sum(content.lower().count(word) for word in emotional_words)
        
        # Personal pronouns (indicates personal experience)
        personal_pronouns = ['i', 'we', 'my', 'our', 'me', 'us']
        personal_count = sum(content.lower().count(' ' + word + ' ') for word in personal_pronouns)
        
        # Call-to-action indicators
        cta_phrases = [
            'comment below', 'let me know', 'share your', 'what do you think',
            'tell us', 'join the discussion', 'your thoughts', 'feedback'
        ]
        cta_count = sum(content.lower().count(phrase) for phrase in cta_phrases)
        
        engagement_score = min(100, (
            question_count * 2 + direct_questions * 5 + action_count + 
            emotional_count * 2 + personal_count + cta_count * 3
        ))
        
        return {
            'question_indicators': question_count,
            'direct_questions': direct_questions,
            'action_words': action_count,
            'emotional_words': emotional_count,
            'personal_pronouns': personal_count,
            'cta_indicators': cta_count,
            'engagement_score': engagement_score,
            'is_engaging': engagement_score > 20
        }
    
    def _calculate_seo_relevance(self, content: str, keywords: List[Dict]) -> float:
        """Calculate SEO relevance score"""
        content_lower = content.lower()
        
        # Check for SEO-related keywords
        seo_mentions = sum(1 for keyword in SEO_KEYWORDS if keyword in content_lower)
        
        # Check for high-value keywords in extracted keywords
        high_value_keywords = 0
        for kw_data in keywords[:10]:  # Top 10 keywords
            if kw_data['word'] in SEO_KEYWORDS:
                high_value_keywords += kw_data['frequency']
        
        # Calculate relevance score (0-100)
        relevance_score = min(100, (seo_mentions * 5) + (high_value_keywords * 3))
        
        return relevance_score
    
    def _identify_comment_opportunities(self, content: str, structure: Dict) -> List[Dict[str, Any]]:
        """Identify opportunities for meaningful comments"""
        opportunities = []
        
        # Questions in content
        if structure['question_count'] > 0:
            opportunities.append({
                'type': 'question_response',
                'description': f"Content contains {structure['question_count']} questions that can be addressed",
                'priority': 'high'
            })
        
        # Controversial or debate topics
        debate_indicators = [
            'controversial', 'debate', 'argue', 'disagree', 'opinion', 'believe',
            'think', 'consider', 'perspective', 'viewpoint'
        ]
        
        debate_mentions = sum(1 for indicator in debate_indicators if indicator in content.lower())
        if debate_mentions > 2:
            opportunities.append({
                'type': 'perspective_sharing',
                'description': "Content discusses debatable topics - opportunity for perspective sharing",
                'priority': 'medium'
            })
        
        # How-to or tutorial content
        if any(phrase in content.lower() for phrase in ['how to', 'step by step', 'tutorial', 'guide']):
            opportunities.append({
                'type': 'experience_sharing',
                'description': "Tutorial content - opportunity to share related experiences",
                'priority': 'high'
            })
        
        # Industry trends or news
        trend_indicators = ['trend', 'latest', 'new', 'update', 'change', 'future', '2024', '2025']
        trend_mentions = sum(1 for indicator in trend_indicators if indicator in content.lower())
        if trend_mentions > 3:
            opportunities.append({
                'type': 'trend_discussion',
                'description': "Content discusses industry trends - opportunity for trend analysis",
                'priority': 'medium'
            })
        
        # Problem-solution content
        problem_indicators = ['problem', 'issue', 'challenge', 'struggle', 'difficult', 'solution']
        problem_mentions = sum(1 for indicator in problem_indicators if indicator in content.lower())
        if problem_mentions > 2:
            opportunities.append({
                'type': 'solution_offering',
                'description': "Content discusses problems - opportunity to offer solutions or alternatives",
                'priority': 'high'
            })
        
        return opportunities
    
    def _calculate_overall_score(
        self, 
        basic_metrics: Dict, 
        readability: Dict, 
        engagement: Dict, 
        seo_relevance: float
    ) -> float:
        """Calculate overall content quality score"""
        
        # Word count score (optimal range: 800-2000 words)
        word_count = basic_metrics.get('word_count', 0)
        if 800 <= word_count <= 2000:
            word_score = 100
        elif 500 <= word_count < 800 or 2000 < word_count <= 3000:
            word_score = 80
        elif 300 <= word_count < 500 or 3000 < word_count <= 5000:
            word_score = 60
        else:
            word_score = 40
        
        # Readability score
        readability_score = 100 if readability.get('is_accessible', False) else 60
        
        # Engagement score
        engagement_score = engagement.get('engagement_score', 0)
        
        # SEO relevance score
        seo_score = seo_relevance
        
        # Weighted overall score
        overall_score = (
            word_score * 0.25 + 
            readability_score * 0.20 + 
            engagement_score * 0.35 + 
            seo_score * 0.20
        )
        
        return min(100, max(0, overall_score))
