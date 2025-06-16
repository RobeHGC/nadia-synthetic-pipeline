#!/usr/bin/env python3
"""
Test Suite for Anonymizer Module
Ensures all PII is properly removed from conversations
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path
import re
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.anonymizer import ConversationAnonymizer


class TestAnonymizer:
    """Comprehensive tests for the anonymizer module"""
    
    @pytest.fixture
    def test_data_dir(self):
        """Return path to test data directory"""
        return Path("data/raw")
    
    @pytest.fixture
    def output_dir(self):
        """Return path to output directory"""
        output = Path("data/anonymized")
        output.mkdir(exist_ok=True)
        return output
    
    @pytest.fixture
    def pii_patterns(self):
        """Define PII patterns to check for"""
        return {
            'email': re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                re.IGNORECASE
            ),
            'phone': re.compile(
                r'(?:'
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|'
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}|'
                r'\+\d{1,3}\s?\d{3}\s?\d{3}\s?\d{4}|'
                r'\b\d{10}\b|'
                r'(?:Tel|Cel|Cell|Phone|WhatsApp):\s*[\d\s\-\+\(\)]+\b'
                r')',
                re.IGNORECASE
            ),
            'social': re.compile(
                r'(?:'
                r'@[A-Za-z0-9_]+|'
                r'(?:IG|Instagram|Twitter|FB|Facebook|Snap|Snapchat):\s*@?[A-Za-z0-9_.]+' 
                r')',
                re.IGNORECASE
            ),
            # Specific names we know were injected
            'test_names': [
                "John Smith", "Mary Johnson", "David Brown", "Jennifer Davis",
                "Juan Pérez", "María García", "Carlos López", "Ana Martínez"
            ]
        }
    
    def check_for_pii(self, text: str, pii_patterns: Dict) -> Dict[str, List[str]]:
        """Check if text contains any PII patterns"""
        found_pii = {
            'emails': [],
            'phones': [],
            'socials': [],
            'names': []
        }
        
        # Check regex patterns
        if pii_patterns['email'].search(text):
            found_pii['emails'] = pii_patterns['email'].findall(text)
        
        if pii_patterns['phone'].search(text):
            found_pii['phones'] = pii_patterns['phone'].findall(text)
            
        if pii_patterns['social'].search(text):
            found_pii['socials'] = pii_patterns['social'].findall(text)
        
        # Check for specific test names
        for name in pii_patterns['test_names']:
            if name.lower() in text.lower():
                found_pii['names'].append(name)
        
        return found_pii
    
    def scan_messages_for_pii(self, messages: List[Dict], pii_patterns: Dict) -> Dict[str, Any]:
        """Scan all messages in a conversation for PII"""
        pii_found = {
            'total_messages_with_pii': 0,
            'pii_details': [],
            'summary': {
                'emails': 0,
                'phones': 0,
                'socials': 0,
                'names': 0
            }
        }
        
        for message in messages:
            if not message.get('text'):
                continue
                
            found = self.check_for_pii(message['text'], pii_patterns)
            
            if any(found[key] for key in found):
                pii_found['total_messages_with_pii'] += 1
                pii_found['pii_details'].append({
                    'message_id': message.get('message_id', 'unknown'),
                    'found_pii': found
                })
                
                # Update summary
                for key in found:
                    pii_found['summary'][key] += len(found[key])
        
        return pii_found
    
    def test_anonymizer_via_subprocess(self, test_data_dir, output_dir, pii_patterns):
        """Test anonymizer by calling it via subprocess (like real usage)"""
        # Test files with injected PII
        test_files = [
            "test_case_rapport_success_with_pii.json",
            "test_case_rapport_fail_with_pii.json"
        ]
        
        for test_file in test_files:
            input_path = test_data_dir / test_file
            output_path = output_dir / f"{test_file.replace('_with_pii', '_anonymized')}"
            
            if not input_path.exists():
                pytest.skip(f"Test file not found: {input_path}")
            
            # Run anonymizer via subprocess
            result = subprocess.run([
                sys.executable,
                "scripts/anonymizer.py",
                "--input", str(input_path),
                "--output", str(output_path),
                "--no-ner"  # For consistent testing
            ], capture_output=True, text=True)
            
            # Check that the command succeeded
            assert result.returncode == 0, f"Anonymizer failed: {result.stderr}"
            
            # Load anonymized data
            with open(output_path, 'r', encoding='utf-8') as f:
                anonymized_data = json.load(f)
            
            # Extract messages based on structure
            if isinstance(anonymized_data, list):
                messages = []
                for conv in anonymized_data:
                    messages.extend(conv.get('messages', []))
            else:
                messages = anonymized_data.get('messages', [])
            
            # Scan for remaining PII
            pii_scan = self.scan_messages_for_pii(messages, pii_patterns)
            
            # Assert no PII remains
            assert pii_scan['total_messages_with_pii'] == 0, \
                f"Found {pii_scan['total_messages_with_pii']} messages with PII in {test_file}:\n" + \
                json.dumps(pii_scan['pii_details'], indent=2)
            
            print(f"✅ {test_file}: All PII successfully removed")
    
    def test_anonymizer_direct_api(self, pii_patterns):
        """Test anonymizer by calling it directly as a module"""
        anonymizer = ConversationAnonymizer(aggressive_mode=False)
        
        # Test with sample messages containing various PII
        test_messages = [
            {
                "message_id": 1,
                "text": "Hi, I'm John Smith, email me at john.smith@gmail.com"
            },
            {
                "message_id": 2,
                "text": "Call me at 555-123-4567 or (867) 555-0123"
            },
            {
                "message_id": 3,
                "text": "Follow me @username or Instagram: @myprofile"
            },
            {
                "message_id": 4,
                "text": "Visit us at 123 Main Street, Suite 200"
            },
            {
                "message_id": 5,
                "text": "Contact María García at +52 867 123 4567"
            }
        ]
        
        # Process each message
        anonymized_messages = []
        for msg in test_messages:
            anonymized = anonymizer.anonymize_message(msg)
            anonymized_messages.append(anonymized)
        
        # Check that PII was replaced
        assert "[EMAIL_REMOVED]" in anonymized_messages[0]['text']
        assert "[PHONE_REMOVED]" in anonymized_messages[1]['text']
        assert "[SOCIAL_REMOVED]" in anonymized_messages[2]['text']
        assert "[ADDRESS_REMOVED]" in anonymized_messages[3]['text']
        assert "[PHONE_REMOVED]" in anonymized_messages[4]['text']
        
        # Verify no original PII remains
        pii_scan = self.scan_messages_for_pii(anonymized_messages, pii_patterns)
        assert pii_scan['total_messages_with_pii'] == 0, \
            f"PII still found: {pii_scan['pii_details']}"
        
        print("✅ Direct API test: All PII successfully removed")
    
    def test_preservation_of_structure(self, test_data_dir, output_dir):
        """Test that anonymizer preserves JSON structure and non-PII content"""
        test_file = "test_case_rapport_success_with_pii.json"
        input_path = test_data_dir / test_file
        output_path = output_dir / "test_structure_preserved.json"
        
        if not input_path.exists():
            pytest.skip(f"Test file not found: {input_path}")
        
        # Load original
        with open(input_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Run anonymizer
        anonymizer = ConversationAnonymizer(aggressive_mode=False)
        anonymizer.process_file(input_path, output_path)
        
        # Load anonymized
        with open(output_path, 'r', encoding='utf-8') as f:
            anonymized_data = json.load(f)
        
        # Check structure is preserved
        assert type(original_data) == type(anonymized_data), "Data type changed"
        
        if isinstance(original_data, list):
            assert len(original_data) == len(anonymized_data), "Number of conversations changed"
            
            for orig_conv, anon_conv in zip(original_data, anonymized_data):
                # Check conversation structure
                assert orig_conv.get('conversation_id') == anon_conv.get('conversation_id')
                assert len(orig_conv.get('messages', [])) == len(anon_conv.get('messages', []))
                
                # Check message structure (non-text fields)
                for orig_msg, anon_msg in zip(orig_conv['messages'], anon_conv['messages']):
                    assert orig_msg.get('message_id') == anon_msg.get('message_id')
                    assert orig_msg.get('timestamp') == anon_msg.get('timestamp')
                    assert orig_msg.get('author') == anon_msg.get('author')
                    assert orig_msg.get('has_emoji') == anon_msg.get('has_emoji')
        
        print("✅ Structure preservation test: JSON structure intact")
    
    def test_statistics_accuracy(self, test_data_dir, output_dir):
        """Test that anonymizer statistics are accurate"""
        test_file = "test_case_rapport_success_with_pii.json"
        input_path = test_data_dir / test_file
        output_path = output_dir / "test_stats.json"
        
        if not input_path.exists():
            pytest.skip(f"Test file not found: {input_path}")
        
        # Run anonymizer and capture stats
        anonymizer = ConversationAnonymizer(aggressive_mode=False)
        result = anonymizer.process_file(input_path, output_path)
        
        stats = result['statistics']
        
        # Verify stats match what we expect
        assert stats['total_pii_removed'] > 0, "No PII was removed"
        assert stats['emails_removed'] > 0, "No emails were removed"
        assert stats['phones_removed'] > 0, "No phones were removed"
        assert stats['socials_removed'] > 0, "No social handles were removed"
        
        # Verify total matches sum of components
        component_sum = (
            stats['emails_removed'] + 
            stats['phones_removed'] + 
            stats['names_removed'] + 
            stats['socials_removed'] + 
            stats['addresses_removed']
        )
        assert stats['total_pii_removed'] == component_sum, \
            f"Total ({stats['total_pii_removed']}) doesn't match sum ({component_sum})"
        
        print(f"✅ Statistics test: Accurate counts - {stats['total_pii_removed']} PII removed")


def test_all():
    """Run all tests and report results"""
    test_instance = TestAnonymizer()
    
    # Setup
    test_data_dir = Path("data/raw")
    output_dir = Path("data/anonymized")
    output_dir.mkdir(exist_ok=True)
    
    # Create patterns
    pii_patterns = test_instance.pii_patterns.__wrapped__(test_instance)
    
    print("\n🧪 Running Anonymizer Test Suite...\n")
    
    try:
        # Test 1: Subprocess test
        print("Test 1: Testing via subprocess...")
        test_instance.test_anonymizer_via_subprocess(test_data_dir, output_dir, pii_patterns)
        
        # Test 2: Direct API test
        print("\nTest 2: Testing direct API...")
        test_instance.test_anonymizer_direct_api(pii_patterns)
        
        # Test 3: Structure preservation
        print("\nTest 3: Testing structure preservation...")
        test_instance.test_preservation_of_structure(test_data_dir, output_dir)
        
        # Test 4: Statistics accuracy
        print("\nTest 4: Testing statistics accuracy...")
        test_instance.test_statistics_accuracy(test_data_dir, output_dir)
        
        print("\n✅ All tests passed! The anonymizer is working correctly.")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    # Run tests
    success = test_all()
    sys.exit(0 if success else 1)