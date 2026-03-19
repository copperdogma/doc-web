#!/usr/bin/env python3
"""
Tests for coarse_segment_patterns_v1: Pattern-based header/footer region detection.

Tests pattern-driven segmentation that identifies regions with consistent header/footer styles.
"""

import json
import os
import tempfile
import unittest

from modules.common.utils import read_jsonl


class TestCoarseSegmentPatternsV1(unittest.TestCase):
    """Test pattern-based segmentation module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.input_file = os.path.join(self.test_dir, "elements_core_typed.jsonl")
        self.output_file = os.path.join(self.test_dir, "pattern_regions.json")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def create_test_elements(self, pages_config):
        """
        Create test elements based on pages_config.
        
        pages_config: dict mapping page_num -> {
            'headers': [list of header texts],
            'footers': [list of footer texts],
            'other': [list of other text]
        }
        """
        elements = []
        seq = 0
        
        for page_num in sorted(pages_config.keys()):
            config = pages_config[page_num]
            
            # Add headers (Page-header at top)
            for header_text in config.get('headers', []):
                elements.append({
                    'id': f'page{page_num}-header-{seq}',
                    'seq': seq,
                    'page': page_num,
                    'kind': 'text',
                    'text': header_text,
                    'layout': {'h_align': 'left', 'y': 0.05},  # Top position
                    'content_type': 'Page-header',
                    'content_type_confidence': 0.9,
                })
                seq += 1
            
            # Add footers (Page-footer at bottom)
            for footer_text in config.get('footers', []):
                elements.append({
                    'id': f'page{page_num}-footer-{seq}',
                    'seq': seq,
                    'page': page_num,
                    'kind': 'text',
                    'text': footer_text,
                    'layout': {'h_align': 'right', 'y': 0.95},  # Bottom position
                    'content_type': 'Page-footer',
                    'content_type_confidence': 0.9,
                })
                seq += 1
            
            # Add other text
            for other_text in config.get('other', []):
                elements.append({
                    'id': f'page{page_num}-other-{seq}',
                    'seq': seq,
                    'page': page_num,
                    'kind': 'text',
                    'text': other_text,
                    'layout': {'h_align': 'center', 'y': 0.5},
                    'content_type': 'Text',
                    'content_type_confidence': 0.5,
                })
                seq += 1
        
        # Save to file
        with open(self.input_file, 'w') as f:
            for elem in elements:
                f.write(json.dumps(elem) + '\n')
        
        return elements
    
    def test_basic_frontmatter_gameplay_transition(self):
        """Test basic transition from frontmatter (bottom numbers) to gameplay (top ranges)."""
        # Pages 1-11: bottom page numbers (frontmatter)
        # Pages 12-20: top section ranges (gameplay)
        pages_config = {
            # Frontmatter: page numbers at bottom
            1: {'footers': ['1'], 'other': ['Title page text']},
            2: {'footers': ['2'], 'other': ['Copyright text']},
            3: {'footers': ['3'], 'other': ['Rules text']},
            4: {'footers': ['4'], 'other': ['More rules']},
            5: {'footers': ['5'], 'other': ['Adventure sheet']},
            6: {'footers': ['6'], 'other': ['Sheet continued']},
            7: {'footers': ['7'], 'other': ['Hints text']},
            8: {'footers': ['8'], 'other': ['More hints']},
            9: {'footers': ['9'], 'other': ['Equipment list']},
            10: {'footers': ['10'], 'other': ['List continued']},
            11: {'footers': ['11'], 'other': ['Final frontmatter']},
            # Gameplay: section ranges at top
            12: {'headers': ['1-3'], 'other': ['Gameplay starts']},
            13: {'headers': ['4-6'], 'other': ['Section 4 text']},
            14: {'headers': ['7-9'], 'other': ['Section 7 text']},
            15: {'headers': ['10-12'], 'other': ['Section 10 text']},
            16: {'headers': ['13-15'], 'other': ['Section 13 text']},
            17: {'headers': ['16-18'], 'other': ['Section 16 text']},
            18: {'headers': ['19-21'], 'other': ['Section 19 text']},
            19: {'headers': ['22-24'], 'other': ['Section 22 text']},
            20: {'headers': ['25-27'], 'other': ['Section 25 text']},
        }
        
        self.create_test_elements(pages_config)
        
        # Run module (will be implemented)
        # For now, just verify test data structure
        elements = list(read_jsonl(self.input_file))
        self.assertEqual(len(elements), sum(len(config.get('headers', [])) + len(config.get('footers', [])) + len(config.get('other', [])) 
                                            for config in pages_config.values()))
        
        # Expected output structure
        expected_regions = [
            {
                'start_page': 1,
                'end_page': 11,
                'pattern_style': 'bottom_page_numbers',
                'description': 'Page numbers consistently at bottom corners',
                'confidence': 0.9,
                'pattern_evidence': {
                    'page_footers': 11,  # All 11 pages have footers
                    'page_headers': 0
                }
            },
            {
                'start_page': 12,
                'end_page': 20,
                'pattern_style': 'top_section_ranges',
                'description': 'Section ranges consistently at top corners',
                'confidence': 0.95,
                'pattern_evidence': {
                    'page_footers': 0,
                    'page_headers': 9  # 9 pages have headers
                }
            }
        ]
        
        # This will be the assertion once module is implemented
        # result = load_pattern_regions(self.output_file)
        # self.assertEqual(len(result['regions']), 2)
        # self.assertEqual(result['regions'][0]['start_page'], 1)
        # self.assertEqual(result['regions'][0]['end_page'], 11)
        # self.assertEqual(result['regions'][0]['pattern_style'], 'bottom_page_numbers')
        # self.assertEqual(result['regions'][1]['start_page'], 12)
        # self.assertEqual(result['regions'][1]['end_page'], 20)
        # self.assertEqual(result['regions'][1]['pattern_style'], 'top_section_ranges')
        
        # Expected output structure
        expected_regions = [
            {
                'start_page': 1,
                'end_page': 11,
                'pattern_style': 'bottom_page_numbers',
                'description': 'Page numbers consistently at bottom corners',
                'confidence': 0.9,
                'pattern_evidence': {
                    'page_footers': 11,  # All pages have footers
                    'page_headers': 0,
                    'total_pages_in_region': 11
                }
            },
            {
                'start_page': 12,
                'end_page': 20,
                'pattern_style': 'top_section_ranges',
                'description': 'Section ranges consistently at top corners',
                'confidence': 0.95,
                'pattern_evidence': {
                    'page_footers': 0,
                    'page_headers': 9,  # 9 pages have headers
                    'total_pages_in_region': 9
                }
            }
        ]
        
        # TODO: Once module is implemented, run it and assert:
        # from modules.portionize.coarse_segment_patterns_v1.main import main
        # import sys
        # sys.argv = ['coarse_segment_patterns_v1', 
        #             '--inputs', self.input_file,
        #             '--out', self.output_file]
        # main()
        # 
        # with open(self.output_file) as f:
        #     result = json.load(f)
        # 
        # self.assertEqual(result['schema_version'], 'pattern_regions_v1')
        # self.assertEqual(len(result['regions']), 2)
        # self.assertEqual(result['regions'][0]['start_page'], 1)
        # self.assertEqual(result['regions'][0]['end_page'], 11)
        # self.assertEqual(result['regions'][0]['pattern_style'], 'bottom_page_numbers')
        # self.assertEqual(result['regions'][1]['start_page'], 12)
        # self.assertEqual(result['regions'][1]['end_page'], 20)
        # self.assertEqual(result['regions'][1]['pattern_style'], 'top_section_ranges')
        
        print("✅ Test data created successfully")
        print(f"   Expected regions: {len(expected_regions)}")
        for region in expected_regions:
            print(f"   - Pages {region['start_page']}-{region['end_page']}: {region['pattern_style']}")
    
    def test_mixed_patterns(self):
        """Test pages with mixed patterns (should have lower confidence)."""
        pages_config = {
            1: {'footers': ['1'], 'headers': ['Title'], 'other': ['Mixed page']},
            2: {'footers': ['2'], 'other': ['Normal footer']},
            3: {'headers': ['3-5'], 'other': ['Normal header']},
        }
        
        self.create_test_elements(pages_config)
        
        # Expected: page 1 should be "mixed" or low confidence
        # Pages 2-3 should form separate regions
        
        elements = list(read_jsonl(self.input_file))
        self.assertGreater(len(elements), 0)
        
        print("✅ Mixed pattern test data created")
    
    def test_no_pattern_region(self):
        """Test region with no clear pattern."""
        pages_config = {
            1: {'other': ['Just text, no headers or footers']},
            2: {'other': ['More text']},
            3: {'other': ['Even more text']},
        }
        
        self.create_test_elements(pages_config)
        
        # Expected: region with pattern_style="no_pattern", low confidence
        
        elements = list(read_jsonl(self.input_file))
        self.assertGreater(len(elements), 0)
        
        print("✅ No pattern test data created")
    
    def test_skipped_pages(self):
        """Test that module handles skipped pages (not all pages have patterns)."""
        pages_config = {
            1: {'footers': ['1']},
            2: {'footers': ['2']},
            3: {'other': ['No pattern']},  # Skipped
            4: {'other': ['No pattern']},  # Skipped
            5: {'headers': ['5-7']},
            6: {'headers': ['8-10']},
        }
        
        self.create_test_elements(pages_config)
        
        # Expected: Should cluster pages 1-2, skip 3-4, cluster 5-6
        # OR: Include 3-4 as "no_pattern" region
        
        elements = list(read_jsonl(self.input_file))
        self.assertGreater(len(elements), 0)
        
        print("✅ Skipped pages test data created")


if __name__ == '__main__':
    unittest.main()
