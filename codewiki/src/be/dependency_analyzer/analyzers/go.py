import json
import logging
import subprocess
import tempfile
import os
from typing import List, Tuple, Optional
from pathlib import Path

from codewiki.src.be.dependency_analyzer.models.core import Node, CallRelationship

logger = logging.getLogger(__name__)

def analyze_go_file(
    file_path: str, content: str, repo_path: Optional[str] = None
) -> Tuple[List[Node], List[CallRelationship]]:
    """
    Analyze a Go file using the compiled coma-go binary.
    
    Args:
        file_path: Path to the Go file
        content: Content of the Go file
        repo_path: Repository root path
        
    Returns:
        tuple: (nodes, relationships)
    """
    # Determine binary path (can be configured via env var or default)
    binary_path = os.environ.get("COMA_GO_PATH", "coma-go")
    
    # coma-go expects the file to exist on disk.
    # Since we have the content, we verify if the file on disk matches or if we need a temp file.
    # For now, we assume the file_path refers to the actual file on disk.
    # If the file_path is relative or abstract, we might need to handle it.
    
    # Construct the command
    # Usage: coma-go -file <path> -repo <repo_path>
    cmd = [binary_path, "-file", file_path]
    if repo_path:
        cmd.extend(["-repo", repo_path])
        
    try:
        # Run the binary and capture stdout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # Parse JSON output from stdout
        output_json = json.loads(result.stdout)
        
        nodes = []
        relationships = []
        
        # Convert JSON dicts to Pydantic models
        for node_data in output_json.get("nodes", []):
            # Ensure required fields match
            nodes.append(Node(**node_data))
            
        for rel_data in output_json.get("call_relationships", []):
            relationships.append(CallRelationship(**rel_data))
            
        return nodes, relationships
        
    except subprocess.CalledProcessError as e:
        logger.error(f"coma-go failed for {file_path}: {e.stderr}")
        return [], []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse coma-go output for {file_path}: {e}")
        return [], []
    except Exception as e:
        logger.error(f"Error analyzing Go file {file_path}: {e}")
        return [], []
