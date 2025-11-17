"""
Startup Advisor - A multi-agent system for creating comprehensive business plans using Qwen3-Max.
"""
import argparse
import json
import os
import sys
from dotenv import load_dotenv
from conversation import MultiAgentConversation

def main():
    """Main entry point for the Startup Advisor application."""
    load_dotenv()
    parser = argparse.ArgumentParser(
        description='Startup Advisor - Multi-agent consultant team for business planning using Qwen3-Max',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate both JSON and HTML formats
  python startup_advisor.py --business_idea "AI-powered fitness app"
  
  # Generate only HTML format
  python startup_advisor.py --business_idea "Sustainable fashion marketplace" --format html
  
  # Generate only JSON format with custom output file
  python startup_advisor.py --business_idea "Food delivery service" --format json --output my_plan.json
  
  # Specify custom output files for both formats
  python startup_advisor.py --business_idea "EdTech platform" --json_output plan.json --html_output plan.html
        """
    )
    
    parser.add_argument(
        '--business_idea',
        type=str,
        required=True,
        help='Brief description of the business idea'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'html', 'both'],
        default='both',
        help='Output format: json, html, or both (default: both)'
    )
    
    parser.add_argument(
        '--json_output',
        type=str,
        default='business_plan.json',
        help='Output file for the JSON business plan (default: business_plan.json)'
    )
    
    parser.add_argument(
        '--html_output',
        type=str,
        default='business_plan.html',
        help='Output file for the HTML business plan (default: business_plan.html)'
    )
    
    # For backward compatibility
    parser.add_argument(
        '--output',
        type=str,
        help='(Deprecated) Use --json_output instead'
    )
    
    args = parser.parse_args()
    
    # Handle backward compatibility for --output flag
    if args.output:
        args.json_output = args.output
        print(f"Note: --output flag is deprecated. Use --json_output instead.")
    
    # Check for API key
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        print("Error: QWEN_API_KEY environment variable not set.")
        print("Please set your Qwen API key:")
        print("  export QWEN_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("=" * 70)
    print("🚀 STARTUP ADVISOR - Multi-Agent Business Planning System")
    print("=" * 70)
    print(f"\n📝 Business Idea: {args.business_idea}")
    print(f"📊 Output Format: {args.format.upper()}")
    if args.format in ['json', 'both']:
        print(f"💾 JSON Output: {args.json_output}")
    if args.format in ['html', 'both']:
        print(f"🌐 HTML Output: {args.html_output}")
    print("\n" + "=" * 70)
    
    try:
        # Create the multi-agent conversation
        conversation = MultiAgentConversation(
            business_idea=args.business_idea,
            api_key=api_key,
            output_format=args.format
        )
        
        # Run the conversation and generate the business plan
        print("\n🤖 Initializing multi-agent system...")
        print("👥 Agents: Strategic Advisor, Financial Advisor, Operations Advisor")
        print("\n⏳ Generating business plan... (this may take 30-60 seconds)\n")
        
        result = conversation.generate_business_plan()
        
        # Save the results based on format
        print("\n" + "=" * 70)
        print("💾 SAVING RESULTS")
        print("=" * 70)
        
        if args.format in ['json', 'both'] and 'json' in result:
            with open(args.json_output, 'w', encoding='utf-8') as f:
                json.dump(result['json'], f, indent=2, ensure_ascii=False)
            print(f"✓ JSON business plan saved to: {args.json_output}")
            print(f"  File size: {os.path.getsize(args.json_output)} bytes")
        
        if args.format in ['html', 'both'] and 'html' in result:
            with open(args.html_output, 'w', encoding='utf-8') as f:
                f.write(result['html'])
            print(f"✓ HTML business plan saved to: {args.html_output}")
            print(f"  File size: {os.path.getsize(args.html_output)} bytes")
        
        print("\n" + "=" * 70)
        print("✅ BUSINESS PLAN GENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        # Print summary
        print("\n📊 SUMMARY:")
        print(f"   Business Idea: {args.business_idea}")
        print(f"   Generated at: {result.get('generated_at', 'N/A')}")
        
        if args.format in ['html', 'both']:
            print(f"\n🌐 To view the HTML business plan:")
            print(f"   Open {args.html_output} in your web browser")
            print(f"   Or run: open {args.html_output}  (macOS)")
            print(f"           xdg-open {args.html_output}  (Linux)")
            print(f"           start {args.html_output}  (Windows)")
        
        if args.format in ['json', 'both']:
            print(f"\n📄 To view the JSON business plan:")
            print(f"   cat {args.json_output}")
            print(f"   Or open it with any text editor or JSON viewer")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERROR OCCURRED")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Your QWEN_API_KEY is valid")
        print("  2. You have internet connection")
        print("  3. The Qwen API service is available")
        import traceback
        print("\nFull error traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
