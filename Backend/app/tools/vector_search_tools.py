"""
Vector Search Tools for Campaign Data Analysis

This module provides vector-based semantic search capabilities over campaign data
stored in Pinecone, with BM25 reranking for improved relevance.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from rank_bm25 import BM25Okapi
import re

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class CampaignVectorSearch:
    """Handles vector search operations with BM25 reranking."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536
        )
        self.index_name = "campaign-optimization"
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize connection to Pinecone vector store."""
        try:
            self.vector_store = PineconeVectorStore(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            logger.info(f"✅ Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Pinecone: {str(e)}")
            raise
    
    def _preprocess_text_for_bm25(self, text: str) -> List[str]:
        """Preprocess text for BM25 tokenization."""
        # Convert to lowercase and split on whitespace and punctuation
        text = text.lower()
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Split and filter out empty strings
        tokens = [token for token in text.split() if token.strip()]
        return tokens
    
    def _rerank_with_bm25(self, query: str, documents: List[Dict], top_k: int = None) -> List[Dict]:
        """Rerank documents using BM25 algorithm."""
        if not documents:
            return documents
        
        # Extract text content for BM25
        doc_texts = []
        for doc in documents:
            # Combine page_content and relevant metadata for better matching
            text_parts = [doc.get('page_content', '')]
            
            # Add relevant metadata fields
            metadata = doc.get('metadata', {})
            if metadata.get('campaign_name'):
                text_parts.append(metadata['campaign_name'])
            if metadata.get('platform'):
                text_parts.append(metadata['platform'])
            if metadata.get('objective'):
                text_parts.append(metadata['objective'])
            if metadata.get('sentiment'):
                text_parts.append(metadata['sentiment'])
            
            combined_text = ' '.join(text_parts)
            doc_texts.append(combined_text)
        
        # Tokenize documents for BM25
        tokenized_docs = [self._preprocess_text_for_bm25(text) for text in doc_texts]
        
        # Create BM25 index
        bm25 = BM25Okapi(tokenized_docs)
        
        # Tokenize query
        tokenized_query = self._preprocess_text_for_bm25(query)
        
        # Get BM25 scores
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # Combine with original similarity scores (if available)
        for i, doc in enumerate(documents):
            original_score = doc.get('similarity_score', 0.0)
            bm25_score = bm25_scores[i]
            
            # Hybrid scoring: combine vector similarity and BM25
            # Normalize BM25 score (simple min-max normalization)
            max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1
            normalized_bm25 = bm25_score / max_bm25
            
            # Weighted combination (70% vector similarity, 30% BM25)
            hybrid_score = 0.7 * original_score + 0.3 * normalized_bm25
            doc['hybrid_score'] = hybrid_score
            doc['bm25_score'] = bm25_score
        
        # Sort by hybrid score
        reranked_docs = sorted(documents, key=lambda x: x['hybrid_score'], reverse=True)
        
        # Return top_k if specified
        if top_k:
            reranked_docs = reranked_docs[:top_k]
        
        return reranked_docs
    
    def search_campaigns(
        self, 
        query: str, 
        filters: Optional[Dict] = None, 
        top_k: int = 10,
        doc_types: Optional[List[str]] = None,
        use_reranking: bool = True
    ) -> List[Dict]:
        """
        Search campaign data with optional filtering and reranking.
        
        Args:
            query: Search query
            filters: Metadata filters (e.g., {"platform": "facebook", "status": "active"})
            top_k: Number of results to return
            doc_types: Filter by document types (e.g., ["campaign", "content"])
            use_reranking: Whether to apply BM25 reranking
        
        Returns:
            List of relevant documents with scores
        """
        try:
            # Build filter dictionary
            search_filters = filters or {}
            
            # Add document type filter if specified
            if doc_types:
                if len(doc_types) == 1:
                    search_filters["doc_type"] = doc_types[0]
                else:
                    # For multiple doc types, we'll filter after retrieval
                    pass
            
            # Perform vector similarity search with higher k for reranking
            search_k = top_k * 3 if use_reranking else top_k
            
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=search_k,
                filter=search_filters
            )
            
            # Convert to dictionary format
            documents = []
            for doc, score in results:
                doc_dict = {
                    'page_content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(1 - score),  # Convert distance to similarity
                    'original_score': float(score)
                }
                documents.append(doc_dict)
            
            # Filter by doc_types if multiple specified
            if doc_types and len(doc_types) > 1:
                documents = [
                    doc for doc in documents 
                    if doc['metadata'].get('doc_type') in doc_types
                ]
            
            # Apply BM25 reranking if requested
            if use_reranking and documents:
                documents = self._rerank_with_bm25(query, documents, top_k)
            else:
                documents = documents[:top_k]
            
            logger.info(f"🔍 Found {len(documents)} results for query: '{query[:50]}...'")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Search error: {str(e)}")
            return []

# Initialize the search instance
_search_instance = None

def get_search_instance():
    """Get or create the search instance."""
    global _search_instance
    if _search_instance is None:
        _search_instance = CampaignVectorSearch()
    return _search_instance

@tool
def search_campaign_data(
    query: str,
    filters: Optional[str] = None,
    top_k: int = 5,
    doc_types: Optional[str] = None
) -> str:
    """
    Search campaign data using semantic vector search with BM25 reranking.
    
    This tool provides powerful semantic search over campaign data including:
    - Campaign performance metrics and analysis
    - Content strategies and creative details
    - Sentiment analysis and engagement insights
    - Performance trends and optimization data
    
    Args:
        query: Natural language search query (e.g., "high performing Facebook campaigns with positive sentiment")
        filters: JSON string of metadata filters (e.g., '{"platform": "facebook", "status": "active"}')
        top_k: Number of results to return (default: 5, max: 20)
        doc_types: Comma-separated document types to search (e.g., "campaign,content,metrics,comments")
    
    Returns:
        Formatted search results with relevance scores and key insights
    
    Examples:
        - "Find high-performing Instagram campaigns with engagement rate > 3%"
        - "Show me content strategies for video campaigns that generated positive sentiment"
        - "What are the trends for campaigns with ROAS > 4.0?"
        - "Find campaigns similar to campaign_id_123 in terms of performance"
    """
    try:
        # Parse filters if provided
        parsed_filters = None
        if filters:
            import json
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                return f"❌ Error: Invalid filters format. Use JSON format like: {{'platform': 'facebook'}}"
        
        # Parse doc_types if provided
        parsed_doc_types = None
        if doc_types:
            parsed_doc_types = [dt.strip() for dt in doc_types.split(',')]
            # Validate doc types
            valid_types = ['campaign', 'content', 'metrics', 'comments']
            invalid_types = [dt for dt in parsed_doc_types if dt not in valid_types]
            if invalid_types:
                return f"❌ Error: Invalid doc_types: {invalid_types}. Valid types: {valid_types}"
        
        # Limit top_k
        top_k = min(max(1, top_k), 20)
        
        # Get search instance and perform search
        search_instance = get_search_instance()
        results = search_instance.search_campaigns(
            query=query,
            filters=parsed_filters,
            top_k=top_k,
            doc_types=parsed_doc_types,
            use_reranking=True
        )
        
        if not results:
            return f"🔍 No results found for query: '{query}'"
        
        # Format results
        formatted_results = []
        formatted_results.append(f"🔍 **Search Results for:** '{query}'")
        formatted_results.append(f"📊 **Found {len(results)} relevant results**")
        formatted_results.append("=" * 60)
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            
            # Header with document type and key info
            doc_type = metadata.get('doc_type', 'unknown').upper()
            header_parts = [f"**{i}. {doc_type}"]
            
            if metadata.get('campaign_id'):
                header_parts.append(f"Campaign: {metadata['campaign_id']}")
            if metadata.get('campaign_name'):
                header_parts.append(f"({metadata['campaign_name']})")
            
            formatted_results.append(" ".join(header_parts) + "**")
            
            # Relevance scores
            similarity = result.get('similarity_score', 0)
            hybrid = result.get('hybrid_score', 0)
            formatted_results.append(f"🎯 **Relevance:** {hybrid:.3f} (Vector: {similarity:.3f})")
            
            # Key metadata
            key_info = []
            if metadata.get('platform'):
                key_info.append(f"Platform: {metadata['platform'].title()}")
            if metadata.get('status'):
                key_info.append(f"Status: {metadata['status'].title()}")
            if metadata.get('performance_tier'):
                key_info.append(f"Performance: {metadata['performance_tier'].replace('_', ' ').title()}")
            if metadata.get('sentiment'):
                key_info.append(f"Sentiment: {metadata['sentiment'].title()}")
            if metadata.get('roas'):
                key_info.append(f"ROAS: {metadata['roas']:.2f}x")
            if metadata.get('engagement_rate'):
                key_info.append(f"Engagement: {metadata['engagement_rate']:.1f}%")
            
            if key_info:
                formatted_results.append(f"📋 **Key Info:** {' | '.join(key_info)}")
            
            # Content preview (first 200 chars)
            content_preview = result['page_content'][:200].strip()
            if len(result['page_content']) > 200:
                content_preview += "..."
            formatted_results.append(f"📄 **Content:** {content_preview}")
            
            formatted_results.append("-" * 40)
        
        # Add search tips
        formatted_results.append("")
        formatted_results.append("💡 **Search Tips:**")
        formatted_results.append("• Use specific metrics: 'ROAS > 4.0', 'engagement rate > 3%'")
        formatted_results.append("• Filter by platform: 'Facebook campaigns' or 'Instagram content'")
        formatted_results.append("• Search by performance: 'high performing', 'low engagement'")
        formatted_results.append("• Analyze sentiment: 'positive sentiment', 'negative comments'")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"❌ Tool error: {str(e)}")
        return f"❌ Error performing search: {str(e)}"

@tool
def search_similar_campaigns(
    campaign_id: str,
    similarity_type: str = "performance",
    top_k: int = 5
) -> str:
    """
    Find campaigns similar to a specific campaign based on different similarity criteria.
    
    Args:
        campaign_id: The ID of the reference campaign
        similarity_type: Type of similarity to search for:
            - "performance": Similar performance metrics (ROAS, CTR, engagement)
            - "content": Similar content strategies and creative approaches
            - "audience": Similar target audience and demographics
            - "overall": Overall similarity across all factors
        top_k: Number of similar campaigns to return (default: 5, max: 15)
    
    Returns:
        List of similar campaigns with similarity explanations
    """
    try:
        # First, find the reference campaign
        search_instance = get_search_instance()
        
        # Search for the specific campaign
        ref_results = search_instance.search_campaigns(
            query=f"campaign_id:{campaign_id}",
            filters={"campaign_id": campaign_id},
            top_k=1,
            doc_types=["campaign"],
            use_reranking=False
        )
        
        if not ref_results:
            return f"❌ Campaign with ID '{campaign_id}' not found"
        
        ref_campaign = ref_results[0]
        ref_metadata = ref_campaign['metadata']
        
        # Build similarity query based on type
        if similarity_type == "performance":
            # Search for campaigns with similar performance metrics
            roas = ref_metadata.get('roas', 0)
            ctr = ref_metadata.get('ctr', 0)
            engagement = ref_metadata.get('engagement_rate', 0)
            
            query = f"campaigns with ROAS around {roas:.1f} CTR around {ctr:.1f}% engagement rate around {engagement:.1f}%"
            
        elif similarity_type == "content":
            # Search for campaigns with similar content approaches
            campaign_type = ref_metadata.get('campaign_type', '')
            objective = ref_metadata.get('objective', '')
            
            query = f"{campaign_type} campaigns with {objective} objective content strategy"
            
        elif similarity_type == "audience":
            # Search for campaigns with similar targeting
            platform = ref_metadata.get('platform', '')
            target_audience = ref_metadata.get('target_audience', '')
            
            query = f"{platform} campaigns targeting {target_audience}"
            
        else:  # overall
            # Comprehensive similarity search
            platform = ref_metadata.get('platform', '')
            objective = ref_metadata.get('objective', '')
            performance_tier = ref_metadata.get('performance_tier', '')
            
            query = f"{platform} {objective} campaigns {performance_tier} performance similar strategy"
        
        # Search for similar campaigns (exclude the reference campaign)
        similar_results = search_instance.search_campaigns(
            query=query,
            top_k=top_k + 5,  # Get extra to filter out reference
            doc_types=["campaign"],
            use_reranking=True
        )
        
        # Filter out the reference campaign
        filtered_results = [
            result for result in similar_results 
            if result['metadata'].get('campaign_id') != campaign_id
        ][:top_k]
        
        if not filtered_results:
            return f"🔍 No similar campaigns found for '{campaign_id}'"
        
        # Format results
        formatted_results = []
        formatted_results.append(f"🔍 **Similar Campaigns to:** {campaign_id}")
        formatted_results.append(f"📊 **Similarity Type:** {similarity_type.title()}")
        formatted_results.append(f"📋 **Reference Campaign:** {ref_metadata.get('campaign_name', 'Unknown')}")
        formatted_results.append("=" * 60)
        
        for i, result in enumerate(filtered_results, 1):
            metadata = result['metadata']
            
            formatted_results.append(f"**{i}. {metadata.get('campaign_name', 'Unknown')} ({metadata.get('campaign_id')})**")
            formatted_results.append(f"🎯 **Similarity Score:** {result.get('hybrid_score', 0):.3f}")
            
            # Show comparison metrics
            comparison = []
            if similarity_type in ["performance", "overall"]:
                ref_roas = ref_metadata.get('roas', 0)
                sim_roas = metadata.get('roas', 0)
                comparison.append(f"ROAS: {sim_roas:.2f}x (ref: {ref_roas:.2f}x)")
                
                ref_ctr = ref_metadata.get('ctr', 0)
                sim_ctr = metadata.get('ctr', 0)
                comparison.append(f"CTR: {sim_ctr:.2f}% (ref: {ref_ctr:.2f}%)")
            
            if similarity_type in ["content", "overall"]:
                comparison.append(f"Type: {metadata.get('campaign_type', 'Unknown')}")
                comparison.append(f"Objective: {metadata.get('objective', 'Unknown')}")
            
            if comparison:
                formatted_results.append(f"📊 **Comparison:** {' | '.join(comparison)}")
            
            # Key differences/similarities
            similarities = []
            if metadata.get('platform') == ref_metadata.get('platform'):
                similarities.append("Same platform")
            if metadata.get('performance_tier') == ref_metadata.get('performance_tier'):
                similarities.append("Same performance tier")
            if metadata.get('sentiment') == ref_metadata.get('sentiment'):
                similarities.append("Same sentiment")
            
            if similarities:
                formatted_results.append(f"✅ **Similarities:** {', '.join(similarities)}")
            
            formatted_results.append("-" * 40)
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"❌ Tool error: {str(e)}")
        return f"❌ Error finding similar campaigns: {str(e)}"

@tool
def analyze_campaign_trends(
    metric: str = "performance",
    time_period: str = "last_30_days",
    platform: Optional[str] = None,
    top_k: int = 10
) -> str:
    """
    Analyze trends and patterns across campaigns based on specific metrics.
    
    Args:
        metric: Metric to analyze trends for:
            - "performance": Overall performance trends (ROAS, CTR, conversions)
            - "engagement": Engagement trends (likes, shares, comments)
            - "sentiment": Sentiment trends and patterns
            - "content": Content type performance trends
            - "budget": Budget utilization and efficiency trends
        time_period: Time period for analysis (currently supports "last_30_days")
        platform: Filter by platform ("facebook", "instagram", or None for all)
        top_k: Number of trend insights to return
    
    Returns:
        Comprehensive trend analysis with insights and recommendations
    """
    try:
        search_instance = get_search_instance()
        
        # Build search query based on metric
        if metric == "performance":
            query = "campaign performance metrics ROAS CTR conversions revenue trends analysis"
        elif metric == "engagement":
            query = "engagement rate likes shares comments social media interaction trends"
        elif metric == "sentiment":
            query = "sentiment analysis positive negative comments feedback trends"
        elif metric == "content":
            query = "content type performance video image carousel story creative trends"
        elif metric == "budget":
            query = "budget utilization spend efficiency cost optimization trends"
        else:
            query = f"{metric} trends analysis patterns insights"
        
        # Add platform filter if specified
        filters = {}
        if platform:
            filters["platform"] = platform.lower()
        
        # Search for relevant data
        results = search_instance.search_campaigns(
            query=query,
            filters=filters,
            top_k=top_k * 2,  # Get more results for analysis
            doc_types=["campaign", "metrics", "comments"] if metric == "sentiment" else ["campaign", "metrics"],
            use_reranking=True
        )
        
        if not results:
            return f"🔍 No data found for {metric} trend analysis"
        
        # Analyze trends
        formatted_results = []
        formatted_results.append(f"📈 **Trend Analysis: {metric.title()}**")
        if platform:
            formatted_results.append(f"🎯 **Platform:** {platform.title()}")
        formatted_results.append(f"⏰ **Period:** {time_period.replace('_', ' ').title()}")
        formatted_results.append("=" * 60)
        
        # Extract and analyze key metrics
        performance_data = []
        sentiment_data = []
        content_data = []
        
        for result in results:
            metadata = result['metadata']
            
            if metric == "performance":
                if metadata.get('roas') and metadata.get('ctr'):
                    performance_data.append({
                        'roas': metadata['roas'],
                        'ctr': metadata['ctr'],
                        'performance_tier': metadata.get('performance_tier', 'unknown'),
                        'campaign_id': metadata.get('campaign_id')
                    })
            
            elif metric == "sentiment":
                if metadata.get('sentiment') and metadata.get('sentiment_score'):
                    sentiment_data.append({
                        'sentiment': metadata['sentiment'],
                        'score': metadata['sentiment_score'],
                        'campaign_id': metadata.get('campaign_id')
                    })
            
            elif metric == "content":
                if metadata.get('content_type'):
                    content_data.append({
                        'type': metadata['content_type'],
                        'performance_tier': metadata.get('performance_tier', 'unknown'),
                        'campaign_id': metadata.get('campaign_id')
                    })
        
        # Generate insights based on metric type
        if metric == "performance" and performance_data:
            # Performance trend insights
            high_performers = [d for d in performance_data if d['performance_tier'] == 'high_performer']
            avg_roas = sum(d['roas'] for d in performance_data) / len(performance_data)
            avg_ctr = sum(d['ctr'] for d in performance_data) / len(performance_data)
            
            formatted_results.append(f"📊 **Performance Overview:**")
            formatted_results.append(f"• Average ROAS: {avg_roas:.2f}x")
            formatted_results.append(f"• Average CTR: {avg_ctr:.2f}%")
            formatted_results.append(f"• High Performers: {len(high_performers)}/{len(performance_data)} ({len(high_performers)/len(performance_data)*100:.1f}%)")
            
        elif metric == "sentiment" and sentiment_data:
            # Sentiment trend insights
            positive = [d for d in sentiment_data if d['sentiment'] == 'positive']
            negative = [d for d in sentiment_data if d['sentiment'] == 'negative']
            neutral = [d for d in sentiment_data if d['sentiment'] == 'neutral']
            
            formatted_results.append(f"😊 **Sentiment Distribution:**")
            formatted_results.append(f"• Positive: {len(positive)}/{len(sentiment_data)} ({len(positive)/len(sentiment_data)*100:.1f}%)")
            formatted_results.append(f"• Neutral: {len(neutral)}/{len(sentiment_data)} ({len(neutral)/len(sentiment_data)*100:.1f}%)")
            formatted_results.append(f"• Negative: {len(negative)}/{len(sentiment_data)} ({len(negative)/len(sentiment_data)*100:.1f}%)")
        
        # Show top insights from search results
        formatted_results.append("")
        formatted_results.append(f"🔍 **Key Insights:**")
        
        for i, result in enumerate(results[:5], 1):
            metadata = result['metadata']
            
            # Extract key insight from content
            content = result['page_content']
            if "TREND ANALYSIS:" in content:
                trend_section = content.split("TREND ANALYSIS:")[1].split("\n")[1:4]
                insight = " | ".join([line.strip() for line in trend_section if line.strip()])
            else:
                # Extract first meaningful line
                lines = content.split('\n')
                insight = next((line.strip() for line in lines if len(line.strip()) > 20), "No specific insight available")[:100]
            
            formatted_results.append(f"{i}. {insight}")
        
        # Add recommendations
        formatted_results.append("")
        formatted_results.append("💡 **Recommendations:**")
        
        if metric == "performance":
            formatted_results.append("• Focus on campaigns with ROAS > 3.0 for scaling")
            formatted_results.append("• Optimize campaigns with CTR < 1.0%")
            formatted_results.append("• Analyze high-performer strategies for replication")
        elif metric == "sentiment":
            formatted_results.append("• Address negative sentiment patterns quickly")
            formatted_results.append("• Amplify content generating positive responses")
            formatted_results.append("• Monitor sentiment changes after campaign updates")
        elif metric == "content":
            formatted_results.append("• Double down on high-performing content types")
            formatted_results.append("• Test variations of successful creative formats")
            formatted_results.append("• Retire consistently underperforming content types")
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"❌ Tool error: {str(e)}")
        return f"❌ Error analyzing trends: {str(e)}"

# Export functions for tool registry
def get_vector_search_tools():
    """Get all vector search tools."""
    return [
        search_campaign_data,
        search_similar_campaigns,
        analyze_campaign_trends
    ] 