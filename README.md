# AI Chat Assistant

A modern, web-based chatbot interface powered by OpenAI's GPT-3.5-turbo model.

## Features

- 🎨 **Modern UI**: Clean, responsive design with TailwindCSS
- 💬 **Real-time Chat**: Instant messaging with AI assistant
- 📚 **Document Knowledge Base**: Upload and process PDFs, DOCX, and TXT files
- 🔍 **Smart Document Search**: AI-powered document retrieval and context
- 🔄 **Chat History**: Maintains conversation context
- 🧹 **Clear Chat**: Reset conversation history
- ♿ **Accessible**: Built with accessibility features
- 📱 **Mobile Responsive**: Works on all device sizes
- ⚡ **Fast**: Optimized for performance with vector database

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in the project root:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. Run the Application

```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Upload Documents**: Click "📄 Upload Docs" to add PDFs, DOCX, or TXT files to your knowledge base
2. **Start a Conversation**: Type your message in the text area and press Enter or click Send
3. **Ask About Documents**: The AI will automatically search your documents and provide relevant answers
4. **Keyboard Shortcuts**: Use `Ctrl+Enter` to send messages quickly
5. **Clear Chat**: Click the "Clear Chat" button to reset the conversation
6. **Document Management**: View your knowledge base summary in the document upload section

## API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message to AI assistant
- `POST /api/clear` - Clear conversation history
- `POST /api/documents/upload` - Upload and process documents
- `POST /api/documents/process` - Process all documents in directory
- `GET /api/documents/summary` - Get document knowledge base summary

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML, TailwindCSS, Alpine.js
- **AI Model**: OpenAI GPT-3.5-turbo
- **Document Processing**: PyPDF2, python-docx, sentence-transformers
- **Vector Database**: ChromaDB for semantic search
- **Styling**: TailwindCSS utility classes
- **Accessibility**: ARIA labels, keyboard navigation, focus management

## File Structure

```
agentchatbot/
├── main.py                 # Flask application
├── document_processor.py   # Document processing and vector search
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── documents/             # Upload your PDFs, DOCX, TXT files here
├── processed/             # Processed document data and vector database
└── templates/
    └── chat.html          # Chat interface template
```

## Security Notes

- Never commit your API key to version control
- Use environment variables for sensitive configuration
- Consider rate limiting for production use

## Troubleshooting

- **API Key Error**: Ensure your OpenAI API key is set correctly
- **Port Already in Use**: Change the port in `main.py` or kill the existing process
- **Module Not Found**: Run `pip install -r requirements.txt`

## License

This project is open source and available under the MIT License. # agentchatbot
