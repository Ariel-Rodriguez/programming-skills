"""
Ollama API Adapter

Imperative Shell: HTTP calls isolated here.
"""

import json
import urllib.request
import urllib.error
from domain import ModelConfig, Result, Success, Failure


class OllamaAdapter:
    """
    Adapter for Ollama API.
    
    Explicit Boundaries: Isolates Ollama-specific logic.
    Error Handling Design: Network errors become Result types.
    """
    
    def call(self, prompt: str, config: ModelConfig) -> Result:
        """
        Call Ollama chat API.
        
        Local Reasoning: All parameters explicit, no hidden config.
        """
        url = f"{config.base_url}/chat/completions"
        data = {
            "model": config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "options": {"num_ctx": config.num_ctx}
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res['choices'][0]['message']['content']
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
        Check if Ollama is running.
        
        Simple boolean check - availability is binary.
        """
        try:
            host = config.base_url.replace('/v1', '')
            urllib.request.urlopen(f"{host}/api/tags", timeout=5)
            return True
        except Exception:
            return False
