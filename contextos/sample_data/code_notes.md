# Code Notes

The parser can detect simple code structures before chunking.

```python
class ContextBuilder:
    def build(self, question, chunks):
        return "prompt"
```

Code structure is captured as metadata so source lines and sections can be shown in search and prompts.
