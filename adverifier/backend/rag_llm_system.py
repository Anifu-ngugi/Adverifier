import os
import openai
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import requests
from bs4 import BeautifulSoup
import json

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

class AdVerificationSystem:
    def __init__(self):
        # Initialize embeddings and LLM
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4")
        
        # Create or load vector database
        self.load_or_create_knowledge_base()
    
    def load_or_create_knowledge_base(self):
        """Load existing knowledge base or create a new one"""
        try:
            self.vectordb = Chroma(
                persist_directory="./chroma_db",
                embedding_function=self.embeddings
            )
            print("Loaded existing knowledge base")
        except:
            # If no existing DB, create an empty one and populate with initial data
            self.vectordb = Chroma(
                persist_directory="./chroma_db",
                embedding_function=self.embeddings
            )
            self.populate_initial_knowledge()
    
    def populate_initial_knowledge(self):
        """Populate the vector database with initial advertising regulations and guidelines"""
        # FTC advertising guidelines
        ftc_guidelines = """
        The Federal Trade Commission (FTC) enforces truth-in-advertising laws. These laws require:
        1. Advertisements must be truthful and non-deceptive
        2. Advertisers must have evidence to back up their claims
        3. Advertisements cannot be unfair
        
        An ad is deceptive if it contains a statement or omits information that is likely to mislead consumers 
        and is material to consumers' decision to buy or use the product.
        
        An ad is unfair if it causes or is likely to cause substantial consumer injury that consumers could not 
        reasonably avoid and that is not outweighed by the benefit to consumers or competition.
        
        Endorsements and testimonials must reflect the honest opinions, findings, beliefs, or experience of the endorser.
        Endorsers must disclose any material connections between themselves and the advertiser.
        """
        
        # Social media advertising rules
        social_media_rules = """
        Social media advertising rules:
        1. Clearly disclose when content is sponsored or paid
        2. Use hashtags like #ad or #sponsored for sponsored content
        3. Influencers must disclose material connections to brands
        4. Claims about products must be truthful and substantiated
        5. Health and medical claims require scientific evidence
        6. Disclosures should be clear, conspicuous, and easily noticed
        7. Contests and promotions must clearly state rules and requirements
        """
        
        # Common misleading advertising tactics
        misleading_tactics = """
        Common misleading advertising tactics:
        1. False claims: Making untrue statements about products
        2. Bait and switch: Advertising one product but substituting another
        3. Hidden fees: Not disclosing all costs upfront
        4. Misleading visuals: Showing unrealistic product results
        5. Ambiguous or unclear language: Using terms like "natural" without clear meaning
        6. False urgency: Creating fake time pressure like "limited time offer"
        7. Fake testimonials: Using paid actors without disclosure
        8. Misleading comparisons: Comparing to inferior products without context
        9. Incomplete information: Omitting key details affecting purchasing decisions
        10. Predatory targeting: Targeting vulnerable populations with misleading claims
        """
        
        # Bundle knowledge sources
        knowledge_sources = [ftc_guidelines, social_media_rules, misleading_tactics]
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        all_chunks = []
        
        for source in knowledge_sources:
            chunks = text_splitter.split_text(source)
            all_chunks.extend(chunks)
        
        # Add to vector database
        self.vectordb.add_texts(all_chunks)
        self.vectordb.persist()
        print(f"Added {len(all_chunks)} text chunks to knowledge base")
    
    def scrape_ad_context(self, url):
        """Scrape additional context from the ad's URL if available"""
        if not url:
            return "No URL provided for additional context."
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text from main content areas
            main_content = ""
            for tag in ['p', 'h1', 'h2', 'h3', 'div', 'span']:
                for element in soup.find_all(tag):
                    if element.text.strip():
                        main_content += element.text.strip() + "\n"
            
            return main_content[:5000]  # Limit context length
        except Exception as e:
            return f"Error scraping URL: {str(e)}"
    
    def verify_advertisement(self, ad_content, ad_url=None):
        """Verify the credibility and authenticity of advertisement content"""
        # Get the retriever from the vector store
        retriever = self.vectordb.as_retriever(search_kwargs={"k": 5})
        
        # Get additional context if URL provided
        url_context = self.scrape_ad_context(ad_url) if ad_url else "No URL provided."
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template("""
        You are an expert in advertisement verification, tasked with assessing the credibility and authenticity of ads.
        
        ADVERTISEMENT TO VERIFY:
        {ad_content}
        
        ADDITIONAL CONTEXT FROM URL:
        {url_context}
        
        RELEVANT ADVERTISING REGULATIONS AND GUIDELINES:
        {context}
        
        Please analyze the advertisement and provide:
        1. A credibility score from 0.0 to 1.0 (where 0 is completely misleading and 1 is fully verified)
        2. A detailed explanation of your assessment
        3. Specific issues or red flags identified
        4. Recommendations for improvement
        
        Format your response as a JSON object with keys: "score", "explanation", "issues", "recommendations"
        """)
        
        # Create the document chain
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # Create the retrieval chain
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        # Run the retrieval chain
        response = retrieval_chain.invoke({
            "ad_content": ad_content,
            "url_context": url_context
        })
        
        # Extract and parse the response
        result = response["answer"]
        try:
            parsed_result = json.loads(result)
            return {
                "credibility_score": parsed_result.get("score", 0.5),
                "explanation": parsed_result.get("explanation", "No explanation provided."),
                "issues": parsed_result.get("issues", []),
                "recommendations": parsed_result.get("recommendations", [])
            }
        except:
            # If JSON parsing fails, return a formatted response
            return {
                "credibility_score": 0.5,
                "explanation": "Could not parse structured result. Raw analysis: " + result,
                "issues": ["Result format error"],
                "recommendations": ["Try again with a different advertisement format"]
            }
