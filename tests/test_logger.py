from core.logger import get_logger

def test_logger():
    print("="*40)
    print("TEST: LOGGING UTILITY")
    print("="*40)
    
    logger = get_logger("test_logger")
    
    print("You should see Info, Warning, and Error logs below:")
    print("-" * 20)
    logger.debug("This is a debug message (hidden by default).")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    print("-" * 20)
    
    print("\n✅ Logger executed successfully.")

if __name__ == "__main__":
    test_logger()
