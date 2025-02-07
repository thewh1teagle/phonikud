"""
uv pip install -e .
"""

from mishkal.g2p import g2p

text = """
 וְגַם
"""

print(g2p(text))

