#!/usr/bin/env python3
"""
Anonymizer Module - Critical Security Component
Removes all PII from conversation data using regex and NER
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Try to import spaCy for NER (optional enhancement)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ spaCy not available. Using regex-only mode.")

class ConversationAnonymizer:
    """
    Anonymizes conversations by removing PII using multiple techniques
    """
    
    def __init__(self, aggressive_mode: bool = True):
        self.aggressive_mode = aggressive_mode
        self.setup_logging()
        self.setup_patterns()
        self.setup_ner()
        
        # Statistics tracking
        self.stats = {
            "emails_removed": 0,
            "phones_removed": 0,
            "names_removed": 0,
            "socials_removed": 0,
            "addresses_removed": 0,
            "total_pii_removed": 0
        }
    
    def setup_logging(self):
        """Configure logging for audit trail"""
        log_file = f"logs/anonymizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        Path("logs").mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ConversationAnonymizer')
        
    def setup_patterns(self):
        """Define regex patterns for PII detection"""
        # Common first and last names for detection
        common_names = [
            # English names
            "John", "Mary", "David", "Jennifer", "Michael", "Sarah", "Robert", "Lisa",
            "James", "Emily", "Andrew", "Jessica", "Smith", "Johnson", "Brown", "Davis",
            "Wilson", "Miller", "Taylor", "Anderson", "Thompson", "White", "Martinez", "Garcia",
            # Spanish names  
            "Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Miguel", "Isabel",
            "Pérez", "García", "López", "Martínez", "Sánchez", "Rodríguez", "Hernández", "González"
        ]
        
        # Create name pattern
        name_pattern = r'\b(?:' + '|'.join(re.escape(name) for name in common_names) + r')\s+(?:' + \
                      '|'.join(re.escape(name) for name in common_names) + r')\b'
        
        self.patterns = {
            # Name patterns (must be before other patterns)
            'name': re.compile(name_pattern, re.IGNORECASE),
            
            # Email patterns
            'email': re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                re.IGNORECASE
            ),
            
            # Phone patterns (multiple formats)
            'phone': re.compile(
                r'(?:'
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|'  # 555-123-4567 or 555.123.4567
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}|'     # (555) 123-4567
                r'\+\d{1,3}\s?\d{3}\s?\d{3}\s?\d{4}|'  # +52 867 123 4567
                r'\b\d{10}\b|'                      # 5551234567
                r'(?:Tel|Cel|Cell|Phone|WhatsApp):\s*[\d\s\-\+\(\)]+\b'  # Tel: 555-1234
                r')',
                re.IGNORECASE
            ),
            
            # Social media handles
            'social': re.compile(
                r'(?:'
                r'@[A-Za-z0-9_]+|'                   # @username
                r'(?:IG|Instagram|Twitter|FB|Facebook|Snap|Snapchat):\s*@?[A-Za-z0-9_.]+' # Platform: username
                r')',
                re.IGNORECASE
            ),
            
            # Addresses (basic pattern)
            'address': re.compile(
                r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Drive|Dr|Road|Rd|Boulevard|Blvd|Lane|Ln|Way|Court|Ct|Plaza|Place|Pl|Calle|Avenida|Av|Blvd|Privada|Col\.|Colonia)\b[^.]*(?:\b\d{5}\b)?',
                re.IGNORECASE
            ),
            
            # URL pattern (for links like fanvue)
            'url': re.compile(
                r'https?://[^\s<>"{}|\\^`\[\]]+',
                re.IGNORECASE
            )
        }
        
        # Replacement tokens
        self.replacements = {
            'name': '[NAME_REMOVED]',
            'email': '[EMAIL_REMOVED]',
            'phone': '[PHONE_REMOVED]',
            'social': '[SOCIAL_REMOVED]',
            'address': '[ADDRESS_REMOVED]',
            'url': '[URL_REMOVED]'
        }
    
    def setup_ner(self):
        """Setup Named Entity Recognition if available"""
        self.nlp = None
        if SPACY_AVAILABLE and self.aggressive_mode:
            try:
                # Try to load Spanish model first (for bilingual support)
                self.nlp = spacy.load("es_core_news_sm")
                self.logger.info("Loaded Spanish spaCy model")
            except:
                try:
                    # Fallback to English model
                    self.nlp = spacy.load("en_core_web_sm")
                    self.logger.info("Loaded English spaCy model")
                except:
                    self.logger.warning("No spaCy model found. Install with: python -m spacy download en_core_web_sm")
                    self.nlp = None
    
    def anonymize_with_regex(self, text: str) -> Tuple[str, Dict[str, int]]:
        """Remove PII using regex patterns"""
        counts = {key: 0 for key in self.patterns}
        
        # Apply each pattern
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                counts[pattern_name] = len(matches)
                text = pattern.sub(self.replacements.get(pattern_name, '[REMOVED]'), text)
                
                # Log what was found (without showing the actual PII)
                self.logger.debug(f"Found {len(matches)} {pattern_name}(s) in text")
        
        return text, counts
    
    def anonymize_with_ner(self, text: str) -> Tuple[str, int]:
        """Remove names using NER"""
        if not self.nlp:
            return text, 0
        
        name_count = 0
        doc = self.nlp(text)
        
        # Build list of name entities to replace
        names_to_replace = []
        for ent in doc.ents:
            if ent.label_ in ["PER", "PERSON"]:  # Person entities
                names_to_replace.append(ent.text)
                name_count += 1
        
        # Replace names (longest first to avoid partial replacements)
        for name in sorted(names_to_replace, key=len, reverse=True):
            text = text.replace(name, self.replacements['name'])
        
        return text, name_count
    
    def anonymize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize a single message"""
        if not message.get("text"):
            return message
        
        original_text = message["text"]
        text = original_text
        
        # Step 1: Regex-based anonymization
        text, regex_counts = self.anonymize_with_regex(text)
        
        # Step 2: NER-based anonymization (if available)
        if self.aggressive_mode and self.nlp:
            text, name_count = self.anonymize_with_ner(text)
            regex_counts['names'] = name_count
        
        # Update statistics
        for key, count in regex_counts.items():
            if key == 'name':
                self.stats['names_removed'] += count
            elif key == 'email':
                self.stats['emails_removed'] += count
            elif key == 'phone':
                self.stats['phones_removed'] += count
            elif key == 'social':
                self.stats['socials_removed'] += count
            elif key == 'address':
                self.stats['addresses_removed'] += count
            elif key == 'url':
                # URLs are counted in total but not in individual stats
                pass
        
        # Create anonymized message
        anonymized_message = message.copy()
        anonymized_message["text"] = text
        
        # Calculate total for statistics (excluding URLs)
        total_removed = sum(count for key, count in regex_counts.items() if key != 'url')
        
        # Add anonymization metadata
        if text != original_text:
            anonymized_message["_anonymized"] = True
            anonymized_message["_pii_removed_count"] = total_removed
            self.stats['total_pii_removed'] += total_removed
            
            # Log anonymization (without showing actual PII)
            self.logger.info(
                f"Message {message.get('message_id', 'unknown')}: "
                f"Removed {total_removed} PII items"
            )
        
        # Remove test metadata if present
        if "_test_pii_added" in anonymized_message:
            del anonymized_message["_test_pii_added"]
        
        return anonymized_message
    
    def anonymize_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize all messages in a conversation"""
        anonymized_conv = conversation.copy()
        
        if "messages" in anonymized_conv:
            anonymized_messages = []
            for message in anonymized_conv["messages"]:
                anonymized_messages.append(self.anonymize_message(message))
            anonymized_conv["messages"] = anonymized_messages
        
        return anonymized_conv
    
    def process_file(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """Process a JSON file containing conversations"""
        self.logger.info(f"Processing file: {input_path}")
        
        # Reset statistics for this file
        self.stats = {key: 0 for key in self.stats}
        
        # Load data
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process based on structure
        if isinstance(data, list):
            # Array of conversations
            anonymized_data = []
            for conv in data:
                anonymized_data.append(self.anonymize_conversation(conv))
        elif isinstance(data, dict) and "messages" in data:
            # Single conversation
            anonymized_data = self.anonymize_conversation(data)
        else:
            raise ValueError(f"Unexpected data structure in {input_path}")
        
        # Save anonymized data
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(anonymized_data, f, indent=2, ensure_ascii=False)
        
        # Log summary
        self.logger.info(
            f"Anonymization complete for {input_path.name}:\n"
            f"  - Emails removed: {self.stats['emails_removed']}\n"
            f"  - Phones removed: {self.stats['phones_removed']}\n"
            f"  - Names removed: {self.stats['names_removed']}\n"
            f"  - Social handles removed: {self.stats['socials_removed']}\n"
            f"  - Addresses removed: {self.stats['addresses_removed']}\n"
            f"  - Total PII removed: {self.stats['total_pii_removed']}"
        )
        
        return {
            "input_file": str(input_path),
            "output_file": str(output_path),
            "statistics": self.stats.copy()
        }


def main():
    """Main entry point for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Anonymize conversations by removing PII"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input JSON file containing conversations"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output file for anonymized conversations"
    )
    parser.add_argument(
        "--no-ner",
        action="store_true",
        help="Disable NER (use regex only)"
    )
    
    args = parser.parse_args()
    
    # Create anonymizer
    anonymizer = ConversationAnonymizer(aggressive_mode=not args.no_ner)
    
    # Process file
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        return 1
    
    try:
        result = anonymizer.process_file(input_path, output_path)
        print(f"\n✅ Anonymization successful!")
        print(f"📄 Output saved to: {output_path}")
        print(f"📊 Total PII removed: {result['statistics']['total_pii_removed']}")
        return 0
    except Exception as e:
        print(f"❌ Error during anonymization: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())