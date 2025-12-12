from bs4 import BeautifulSoup, Comment
import re

class DOMCleaner:
    """
    Cleaning logic to produce a token-efficient, structural representation of the page.
    """
    
    ALLOWED_ATTRS = {
        'id', 'name', 'class', 'type', 'placeholder', 'aria-label', 
        'role', 'href', 'title', 'value', 'data-test', 'data-testid', 
        'alt', 'for'
    }

    @staticmethod
    def clean_dom(html_content: str, max_tokens: int = 8000) -> str:
        """
        Parses HTML, removes noise, and returns a simplified HTML string.
        """
        if not html_content:
            return ""

        soup = BeautifulSoup(html_content, 'html.parser')

        # 1. Remove specific noisy tags completely
        for tag in soup(["script", "style", "noscript", "meta", "head", "svg", "path", "link", "iframe", "img", "video"]):
            tag.decompose()

        # 2. Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 3. Clean Attributes
        for tag in soup.find_all(True):
            current_attrs = dict(tag.attrs)
            tag.attrs = {k: v for k, v in current_attrs.items() if k in DOMCleaner.ALLOWED_ATTRS}

        cleaned_html = str(soup)
        
        # 4. Collapse Whitespace
        cleaned_html = re.sub(r'\n\s*\n', '\n', cleaned_html)
        cleaned_html = re.sub(r'\s+', ' ', cleaned_html)
        
        # 5. Safety Truncation
        # Limit roughly based on char count (1 token approx 4 chars)
        limit = max_tokens * 4
        if len(cleaned_html) > limit:
            cleaned_html = cleaned_html[:limit]
            
            # Basic repair: remove incomplete tag at the end
            last_open = cleaned_html.rfind('<')
            last_close = cleaned_html.rfind('>')
            if last_open > last_close:
                cleaned_html = cleaned_html[:last_open]

        return cleaned_html