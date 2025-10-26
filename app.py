import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Fix warning

import uvicorn
from api.index import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))  # Hugging Face uses 7860
    uvicorn.run(app, host="0.0.0.0", port=port)
