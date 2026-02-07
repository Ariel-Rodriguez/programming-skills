"""
Ollama API Adapter

Imperative Shell: HTTP calls isolated here.
Supports both local Ollama and Ollama Cloud.
"""

import json
import os
import urllib.request
import urllib.error
from domain import ModelConfig, Result, Success, Failure


class OllamaAdapter:
    """
    Adapter for Ollama API (local or cloud).
    
    Explicit Boundaries: Isolates Ollama-specific logic.
    Error Handling Design: Network errors become Result types.
    """
    
    def __init__(self, use_cloud: bool = None, model_name: str = None):
        """
        Initialize adapter.

        Args:
            use_cloud: Use Ollama Cloud instead of local instance
                      If None, auto-detect based on model name
            model_name: Model name for auto-detection
        """
        # Auto-detect cloud usage: if model ends with "cloud" and use_cloud not specified
        if use_cloud is None and model_name:
            self.use_cloud = model_name.lower().endswith("-cloud") or model_name.lower().endswith("cloud")
        else:
            self.use_cloud = use_cloud or False
    
    def call(self, prompt: str, config: ModelConfig) -> Result:
        """
        Call Ollama chat API.
        
        Local Reasoning: All parameters explicit, no hidden config.
        """
        # Determine base URL and headers
        if self.use_cloud:
            base_url = "https://ollama.com"
            api_key = os.environ.get('OLLAMA_API_KEY')
            if not api_key:
                return Failure(
                    "OLLAMA_API_KEY environment variable not set for cloud access",
                    {"use_cloud": True}
                )
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        else:
            base_url = config.base_url
            headers = {'Content-Type': 'application/json'}
        
        url = f"{base_url}/api/chat"
        data = {
            "model": config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_ctx": config.num_ctx}
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res['message']['content']
                return Success(content)
        
        except urllib.error.HTTPError as e:
            return Failure(
                f"Ollama HTTP error: {e.code}",
                {"url": url, "code": e.code}
            )
        except urllib.error.URLError as e:
            return Failure(
                f"Ollama connection failed",
                {"url": url, "reason": str(e.reason)}
            )
        except json.JSONDecodeError as e:
            return Failure(
                "Invalid JSON response from Ollama",
                {"error": str(e)}
            )
        except KeyError as e:
            return Failure(
                "Unexpected response format from Ollama",
                {"missing_key": str(e)}
            )
        except Exception as e:
            return Failure(
                f"Ollama API call failed",
                {"error": str(e), "type": type(e).__name__}
            )
    
    def is_available(self, config: ModelConfig) -> bool:
        """
        Check if Ollama is available.
        """
        if self.use_cloud:
            # For cloud, just check if API key is set
            return os.environ.get('OLLAMA_API_KEY') is not None
        
        # For local, check if server is running
        try:
            host = config.base_url.replace('/v1', '')
            urllib.request.urlopen(f"{host}/api/tags", timeout=5)
            return True
        except Exception:
            return False
