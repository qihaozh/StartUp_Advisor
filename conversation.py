"""
Multi-Agent Conversation Protocol implementation for coordinating advisor agents using Qwen3-Max.
"""
import datetime
import requests
import json
import os
from typing import Dict, Any

class MultiAgentConversation:
    """Manages conversations between multiple agents using Qwen3-Max."""
    
    def __init__(self, business_idea: str, api_key: str = None, output_format: str = 'both'):
        """
        Initialize the multi-agent conversation.
        
        Args:
            business_idea: Description of the business idea
            api_key: API key for Qwen (defaults to environment variable)
            output_format: Output format - 'json', 'html', or 'both'
        """
        self.business_idea = business_idea
        self.api_key = api_key or os.getenv("QWEN_API_KEY")
        self.output_format = output_format
        self.api_endpoint = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_business_plan(self) -> Dict[str, Any]:
        """
        Generate a complete business plan using Qwen3-Max.
        
        Returns:
            A dictionary containing the business plan in requested format(s)
        """
        print(f"Starting business plan generation using Qwen3-Max (format: {self.output_format})...")
        
        # Define the roles for each advisor
        strategic_advisor_role = """
        You are a Strategic Advisor specializing in market analysis, competitive positioning, and long-term business strategy. 
        You help startups identify market opportunities, develop unique value propositions, and create sustainable competitive advantages.
        """
        
        financial_advisor_role = """
        You are a Financial Advisor specializing in startup financial planning, fundraising strategies, cash flow management, and financial projections. 
        You help startups build sustainable financial models, understand funding requirements, and develop investor-ready financial plans.
        """
        
        operations_advisor_role = """
        You are an Operations Advisor specializing in operational planning, supply chain management, resource allocation, and process optimization. 
        You help startups build efficient operational systems, identify key resources, and develop scalable processes.
        """
        
        # Prepare format-specific instructions
        format_instruction = self._get_format_instruction()
        
        # Set up the multi-agent conversation with Qwen3-Max
        system_prompt = """
        You are facilitating a multi-agent conversation between three expert advisors to create a comprehensive business plan.
        """
        
        user_prompt = f"""
        You are facilitating a multi-agent conversation between three expert advisors to create a comprehensive business plan for the following business idea:
        
        BUSINESS IDEA: {self.business_idea}
        
        The conversation will proceed through the following phases:
        1. Initial Analysis: Each advisor provides an initial assessment of the business idea
        2. Strategic Planning: Focus on market positioning, competitive advantage, and growth strategy
        3. Financial Planning: Focus on funding requirements, revenue projections, and financial metrics
        4. Operational Planning: Focus on resource requirements, processes, and implementation timeline
        5. Integration: Integrate all plans and identify any conflicts or gaps
        6. Finalization: Address remaining issues and create an executive summary
        
        For each phase, you'll coordinate the conversation between the three advisors, ensuring they build on each other's insights.
        
        The three advisors are:
        
        Strategic Advisor: {strategic_advisor_role}
        
        Financial Advisor: {financial_advisor_role}
        
        Operations Advisor: {operations_advisor_role}
        
        Please ensure each advisor contributes their expertise to the business plan. The conversation should be collaborative,
        with advisors building on each other's ideas and addressing potential conflicts or gaps.
        
        The final business plan should include:
        1. Executive Summary
        2. Strategic Plan (market analysis, competitive positioning, growth strategy)
        3. Financial Plan (funding requirements, revenue model, projections, metrics)
        4. Operational Plan (resources, processes, timeline, risk mitigation)
        
        {format_instruction}
        """
        
        payload = {
            "model": "qwen3-max",
            "input": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            },
            "parameters": {
                "max_tokens": 8192,
                "temperature": 0.7,
                "top_p": 0.95,
            }
        }
        
        # Generate the business plan using Qwen3-Max
        response = requests.post(
            self.api_endpoint,
            headers=self.headers,
            data=json.dumps(payload)
        )
        
        response_json = response.json()
        
        # Print the response structure for debugging
        print("API Response Structure:", json.dumps(response_json, indent=2)[:500] + "...")
        
        # Extract the response text
        business_plan_text = self._extract_response_text(response_json)
        
        # Prepare result based on output format
        result = {
            'business_idea': self.business_idea,
            'generated_at': self._get_timestamp()
        }
        
        if self.output_format in ['html', 'both']:
            result['html'] = business_plan_text if self._is_html(business_plan_text) else self._convert_to_html(business_plan_text)
            print("✓ HTML format generated")
        
        if self.output_format in ['json', 'both']:
            result['json'] = self._parse_business_plan(business_plan_text)
            print("✓ JSON format generated")
        
        print("\nBusiness plan generation completed!")
        return result
    
    def _get_format_instruction(self) -> str:
        """Get format-specific instructions for the prompt."""
        if self.output_format in ['html', 'both']:
            return """
        
        **OUTPUT FORMAT REQUIREMENT:**
        Please provide the complete business plan as a professional, well-formatted HTML document with the following specifications:
        
        1. **HTML Structure:**
           - Complete HTML5 document (<!DOCTYPE html>, <html>, <head>, <body>)
           - Proper meta tags for charset and viewport
           - Descriptive title tag
        
        2. **Styling Requirements:**
           - Embedded CSS in <style> tags within <head>
           - Professional color scheme (use blues, grays, and accent colors)
           - Clean, modern typography (system fonts)
           - Responsive design (max-width container, proper spacing)
           - Print-friendly layout
        
        3. **Content Structure:**
           - Main heading (h1) with business name/idea
           - Clear section divisions with h2 headings
           - Subsections with h3 headings
           - Use tables for financial data, timelines, and metrics
           - Use lists (ul/ol) for key points and recommendations
           - Highlight important information with styled divs/spans
        
        4. **Visual Elements:**
           - Section dividers or borders
           - Color-coded sections (e.g., different background for each major section)
           - Icons or symbols using Unicode characters (✓, ★, →, etc.)
           - Proper spacing and padding for readability
        
        5. **Required Sections (each in its own styled div):**
           - Executive Summary (with key highlights)
           - Strategic Plan (with market analysis table)
           - Financial Plan (with projections table)
           - Operational Plan (with timeline table)
           - Risk Analysis
           - Conclusion/Next Steps
        
        The HTML should be production-ready, visually appealing, and suitable for presentation to investors or stakeholders.
        Make it look professional and polished, similar to a consulting firm's deliverable.
        """
        else:
            return """
        Please provide the business plan in a well-structured text format with clear sections and subsections.
        """
    
    def _extract_response_text(self, response_json: Dict) -> str:
        """
        Extract the response text from the Qwen API response.
        
        Args:
            response_json: The JSON response from Qwen API
            
        Returns:
            The extracted text content
        """
        try:
            # Primary path: Qwen API standard response structure
            # Response format: {"output": {"choices": [{"message": {"content": "..."}}]}}
            if "output" in response_json and "choices" in response_json["output"]:
                choices = response_json["output"]["choices"]
                if len(choices) > 0 and "message" in choices[0]:
                    content = choices[0]["message"].get("content", "")
                    if content:
                        print("✓ Content extracted from output.choices[0].message.content")
                        return content
            
            # Fallback path 1: output.text (alternative Qwen API format)
            if "output" in response_json and "text" in response_json["output"]:
                print("✓ Content extracted from output.text")
                return response_json["output"]["text"]
            
            # Fallback path 2: choices at root level (OpenAI-compatible format)
            if "choices" in response_json and len(response_json["choices"]) > 0:
                if "message" in response_json["choices"][0]:
                    content = response_json["choices"][0]["message"].get("content", "")
                    if content:
                        print("✓ Content extracted from choices[0].message.content")
                        return content
                elif "text" in response_json["choices"][0]:
                    print("✓ Content extracted from choices[0].text")
                    return response_json["choices"][0]["text"]
            
            # Fallback path 3: data.text (some API variations)
            if "data" in response_json and "text" in response_json["data"]:
                print("✓ Content extracted from data.text")
                return response_json["data"]["text"]
            
            # Fallback path 4: result.text (some API variations)
            if "result" in response_json and "text" in response_json["result"]:
                print("✓ Content extracted from result.text")
                return response_json["result"]["text"]
            
            # Fallback path 5: direct response field
            if "response" in response_json:
                print("✓ Content extracted from response field")
                return response_json["response"]
            
            # If no standard path works, print the response structure for debugging
            print("⚠️ Warning: Could not extract content from standard paths")
            print("Response structure (first 1000 chars):")
            print(json.dumps(response_json, indent=2, ensure_ascii=False)[:1000])
            print("...")
            
            # Last resort: convert entire response to string
            print("⚠️ Using entire response as fallback")
            return str(response_json)
            
        except Exception as e:
            print(f"❌ Error extracting text from response: {e}")
            print(f"Exception type: {type(e).__name__}")
            # Return the full response as string to avoid data loss
            return str(response_json)

    
    def _is_html(self, text: str) -> bool:
        """Check if the text is already in HTML format."""
        return "<!DOCTYPE html>" in text or "<html" in text.lower()
    
    def _convert_to_html(self, text: str) -> str:
        """Convert plain text business plan to HTML format."""
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Plan - {self.business_idea[:50]}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 5px solid #3498db;
            font-size: 1.8em;
        }}
        
        h3 {{
            color: #546e7a;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 20px;
            background-color: #fafafa;
            border-radius: 5px;
        }}
        
        .executive-summary {{
            background-color: #e3f2fd;
            border-left: 5px solid #2196f3;
            padding: 25px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}
        
        .strategic-plan {{
            background-color: #f3e5f5;
            border-left: 5px solid #9c27b0;
        }}
        
        .financial-plan {{
            background-color: #e8f5e9;
            border-left: 5px solid #4caf50;
        }}
        
        .operational-plan {{
            background-color: #fff3e0;
            border-left: 5px solid #ff9800;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        .highlight {{
            background-color: #fff9c4;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #fbc02d;
        }}
        
        .metadata {{
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
        }}
        
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 1.8em;
            }}
            h2 {{
                font-size: 1.4em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Business Plan: {self.business_idea}</h1>
        
        <div class="section executive-summary">
            <h2>📋 Executive Summary</h2>
            <div class="content">
                {self._format_section_content(text, "executive summary")}
            </div>
        </div>
        
        <div class="section strategic-plan">
            <h2>🎯 Strategic Plan</h2>
            <div class="content">
                {self._format_section_content(text, "strategic plan")}
            </div>
        </div>
        
        <div class="section financial-plan">
            <h2>💰 Financial Plan</h2>
            <div class="content">
                {self._format_section_content(text, "financial plan")}
            </div>
        </div>
        
        <div class="section operational-plan">
            <h2>⚙️ Operational Plan</h2>
            <div class="content">
                {self._format_section_content(text, "operational plan")}
            </div>
        </div>
        
        <div class="metadata">
            <p><strong>Generated:</strong> {self._get_timestamp()}</p>
            <p><strong>Generated by:</strong> Multi-Agent Startup Advisor (Qwen3-Max)</p>
        </div>
    </div>
</body>
</html>"""
        return html_template
    
    def _format_section_content(self, text: str, section_name: str) -> str:
        """Format section content for HTML."""
        # Simple formatting - convert line breaks to paragraphs
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Check if it's a heading
                if line.isupper() or line.endswith(':'):
                    formatted.append(f'<h3>{line}</h3>')
                # Check if it's a list item
                elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    formatted.append(f'<li>{line[1:].strip()}</li>')
                else:
                    formatted.append(f'<p>{line}</p>')
        
        return '\n'.join(formatted)
    
    def _parse_business_plan(self, business_plan_text: str) -> Dict[str, Any]:
        """
        Parse the business plan text into a structured dictionary.
        
        Args:
            business_plan_text: The business plan text from Qwen3-Max
            
        Returns:
            A structured business plan dictionary
        """
        # Create a basic structure for the business plan
        business_plan = {
            "business_idea": self.business_idea,
            "executive_summary": "",
            "strategic_plan": {
                "market_analysis": "",
                "competitive_positioning": "",
                "growth_strategy": "",
                "recommendations": ""
            },
            "financial_plan": {
                "funding_requirements": "",
                "revenue_projections": "",
                "cost_structure": "",
                "break_even_analysis": "",
                "financial_metrics": ""
            },
            "operational_plan": {
                "resource_requirements": "",
                "processes": "",
                "timeline": "",
                "risk_mitigation": ""
            },
            "generated_at": self._get_timestamp(),
            "full_plan_text": business_plan_text  # Store the complete text as well
        }
        
        # Try to extract sections from the business plan text
        # This is a simple extraction method - in a production system, you might want to use more sophisticated parsing
        
        # Extract executive summary
        if "EXECUTIVE SUMMARY" in business_plan_text.upper():
            parts = business_plan_text.upper().split("EXECUTIVE SUMMARY")
            if len(parts) > 1:
                exec_summary = parts[1].split("\n\n")[0].strip()
                business_plan["executive_summary"] = exec_summary
        elif "Executive Summary" in business_plan_text:
            parts = business_plan_text.split("Executive Summary")
            if len(parts) > 1:
                exec_summary = parts[1].split("\n\n")[0].strip()
                business_plan["executive_summary"] = exec_summary
        
        # Extract strategic plan sections
        if "MARKET ANALYSIS" in business_plan_text.upper():
            parts = business_plan_text.upper().split("MARKET ANALYSIS")
            if len(parts) > 1:
                market_analysis = parts[1].split("\n\n")[0].strip()
                business_plan["strategic_plan"]["market_analysis"] = market_analysis
        elif "Market Analysis" in business_plan_text:
            parts = business_plan_text.split("Market Analysis")
            if len(parts) > 1:
                market_analysis = parts[1].split("\n\n")[0].strip()
                business_plan["strategic_plan"]["market_analysis"] = market_analysis
        
        if "COMPETITIVE POSITIONING" in business_plan_text.upper():
            parts = business_plan_text.upper().split("COMPETITIVE POSITIONING")
            if len(parts) > 1:
                competitive_positioning = parts[1].split("\n\n")[0].strip()
                business_plan["strategic_plan"]["competitive_positioning"] = competitive_positioning
        elif "Competitive Positioning" in business_plan_text:
            parts = business_plan_text.split("Competitive Positioning")
            if len(parts) > 1:
                competitive_positioning = parts[1].split("\n\n")[0].strip()
                business_plan["strategic_plan"]["competitive_positioning"] = competitive_positioning
        
        # Extract financial plan sections
        if "FUNDING REQUIREMENTS" in business_plan_text.upper():
            parts = business_plan_text.upper().split("FUNDING REQUIREMENTS")
            if len(parts) > 1:
                funding_requirements = parts[1].split("\n\n")[0].strip()
                business_plan["financial_plan"]["funding_requirements"] = funding_requirements
        elif "Funding Requirements" in business_plan_text:
            parts = business_plan_text.split("Funding Requirements")
            if len(parts) > 1:
                funding_requirements = parts[1].split("\n\n")[0].strip()
                business_plan["financial_plan"]["funding_requirements"] = funding_requirements
        
        if "REVENUE PROJECTIONS" in business_plan_text.upper():
            parts = business_plan_text.upper().split("REVENUE PROJECTIONS")
            if len(parts) > 1:
                revenue_projections = parts[1].split("\n\n")[0].strip()
                business_plan["financial_plan"]["revenue_projections"] = revenue_projections
        elif "Revenue Projections" in business_plan_text:
            parts = business_plan_text.split("Revenue Projections")
            if len(parts) > 1:
                revenue_projections = parts[1].split("\n\n")[0].strip()
                business_plan["financial_plan"]["revenue_projections"] = revenue_projections
        
        # Extract operational plan sections
        if "RESOURCE REQUIREMENTS" in business_plan_text.upper():
            parts = business_plan_text.upper().split("RESOURCE REQUIREMENTS")
            if len(parts) > 1:
                resource_requirements = parts[1].split("\n\n")[0].strip()
                business_plan["operational_plan"]["resource_requirements"] = resource_requirements
        elif "Resource Requirements" in business_plan_text:
            parts = business_plan_text.split("Resource Requirements")
            if len(parts) > 1:
                resource_requirements = parts[1].split("\n\n")[0].strip()
                business_plan["operational_plan"]["resource_requirements"] = resource_requirements
        
        if "IMPLEMENTATION TIMELINE" in business_plan_text.upper():
            parts = business_plan_text.upper().split("IMPLEMENTATION TIMELINE")
            if len(parts) > 1:
                timeline = parts[1].split("\n\n")[0].strip()
                business_plan["operational_plan"]["timeline"] = timeline
        elif "Implementation Timeline" in business_plan_text:
            parts = business_plan_text.split("Implementation Timeline")
            if len(parts) > 1:
                timeline = parts[1].split("\n\n")[0].strip()
                business_plan["operational_plan"]["timeline"] = timeline
        
        # If we couldn't extract structured sections, store the full text in the executive summary
        if not business_plan["executive_summary"]:
            business_plan["executive_summary"] = business_plan_text
        
        return business_plan
    
    def _get_timestamp(self) -> str:
        """
        Get the current timestamp.
        
        Returns:
            The current timestamp as a string
        """
        return datetime.datetime.now().isoformat()
