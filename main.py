from flask import Flask, render_template, request, jsonify
import openai
import os
from datetime import datetime
from document_processor import DocumentProcessor

app = Flask(__name__)

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize document processor
doc_processor = DocumentProcessor()

# Initialize conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant with access to a knowledge base of documents. When answering questions, use information from the documents when relevant and cite the source. Be concise, friendly, and provide accurate information."}
]

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat API requests"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Search documents for relevant information
        relevant_docs = doc_processor.search_documents(user_message, n_results=3)
        
        # Create context from relevant documents
        context = ""
        if relevant_docs:
            context = "Based on the available documents, here's what I found:\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                context += f"Source {i} ({doc['metadata']['file_name']}):\n{doc['content'][:300]}...\n\n"
        
        # Create enhanced prompt with document context
        enhanced_message = user_message
        if context:
            enhanced_message = f"Context from documents:\n{context}\n\nUser question: {user_message}"
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": enhanced_message})
        
        # Get response from OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            max_tokens=800
        )
        
        assistant_response = completion.choices[0].message.content
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return jsonify({
            'response': assistant_response,
            'timestamp': datetime.now().isoformat(),
            'sources_used': [doc['metadata']['file_name'] for doc in relevant_docs] if relevant_docs else []
        })
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear conversation history"""
    global conversation_history
    conversation_history = [
        {"role": "system", "content": "You are a helpful AI assistant with access to a knowledge base of documents. When answering questions, use information from the documents when relevant and cite the source. Be concise, friendly, and provide accurate information."}
    ]
    return jsonify({'message': 'Chat history cleared'})

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file to documents directory
        file_path = os.path.join('documents', file.filename)
        file.save(file_path)
        
        # Process the document
        success = doc_processor.process_document(file_path)
        
        if success:
            return jsonify({
                'message': f'Document {file.filename} uploaded and processed successfully',
                'filename': file.filename
            })
        else:
            return jsonify({'error': f'Failed to process document {file.filename}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/documents/process', methods=['POST'])
def process_all_documents():
    """Process all documents in the documents directory"""
    try:
        results = doc_processor.process_all_documents()
        return jsonify({
            'message': 'Document processing completed',
            'results': results
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/api/documents/summary', methods=['GET'])
def get_document_summary():
    """Get summary of processed documents"""
    try:
        summary = doc_processor.get_document_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)