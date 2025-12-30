"""
Configuration management for EcoMetrics application.
Centralizes all environment variables and settings.
"""
import os


class Config:
    """Base configuration class"""
   
    # Application Settings
    APP_NAME = "EcoMetrics"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
   
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
   
    # Receiver Settings
    RECEIVER_HOST = os.getenv("RECEIVER_HOST", "localhost")
    RECEIVER_PORT = int(os.getenv("RECEIVER_PORT", 5000))
    RECEIVER_URL = f"http://{RECEIVER_HOST}:{RECEIVER_PORT}"
   
    # Sender Settings  
    SENDER_INTERVAL = int(os.getenv("SENDER_INTERVAL", 1))  # seconds between data points
    SENDER_HOST = os.getenv("SENDER_HOST", "localhost")
    SENDER_PORT = int(os.getenv("SENDER_PORT", 5001))
   
    # Data Generation Settings
    NUM_SENSORS = int(os.getenv("NUM_SENSORS", 5))
    POLLUTION_MIN = float(os.getenv("POLLUTION_MIN", 0.0))
    POLLUTION_MAX = float(os.getenv("POLLUTION_MAX", 100.0))
   
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
   
    @classmethod
    def display_config(cls):
        """Display current configuration (for debugging)"""
        print(f"=== {cls.APP_NAME} Configuration ===")
        print(f"Version: {cls.VERSION}")
        print(f"Debug Mode: {cls.DEBUG}")
        print(f"Host: {cls.HOST}:{cls.PORT}")
        print(f"Receiver URL: {cls.RECEIVER_URL}")
        print(f"Sender Interval: {cls.SENDER_INTERVAL}s")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 40)


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
   
    # In production, use service names from Docker/K8s
    RECEIVER_HOST = os.getenv("RECEIVER_HOST", "receiver-service")
    RECEIVER_PORT = int(os.getenv("RECEIVER_PORT", 5000))


class TestConfig(Config):
    """Testing-specific configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    SENDER_INTERVAL = 0  # No delay in tests


# Configuration selector
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
}

# Get current environment
ENV = os.getenv("ENVIRONMENT", "development")
current_config = config_by_name.get(ENV, DevelopmentConfig)