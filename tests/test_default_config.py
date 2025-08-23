"""
Test that the default configuration meets security requirements
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_default_config_security():
    """Test that default config meets security requirements"""
    print("🔧 Testing Default Configuration Security")
    print("=" * 50)
    
    try:
        from app.config import config
        
        print(f"Default APPROVAL_TOKEN_SECRET length: {len(config.APPROVAL_TOKEN_SECRET)}")
        
        if len(config.APPROVAL_TOKEN_SECRET) < 32:
            print(f"❌ Default config fails security requirement: {config.APPROVAL_TOKEN_SECRET}")
            return False
        
        print("✅ Default configuration meets 32-character minimum")
        print(f"✅ Token secret: '{config.APPROVAL_TOKEN_SECRET[:20]}...'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing default config: {e}")
        return False

if __name__ == '__main__':
    success = test_default_config_security()
    sys.exit(0 if success else 1)