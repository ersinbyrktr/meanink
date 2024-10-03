import os

import nltk
import numpy as np
from flask import Flask, render_template, request
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, \
    load_index_from_storage, Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import NodeRelationship, TextNode
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index.llms.openai import OpenAI

from app.config import config

os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

nltk.download('punkt')
nltk.download('punkt_tab')

app = Flask(__name__)

# Global variables to store the index and embedding model
index: VectorStoreIndex = VectorStoreIndex(embed_model=Settings.embed_model)
# Define the storage directory
index_storage_dir = './index_storage'
index.storage_context.persist(persist_dir=index_storage_dir)


# Function to initialize the index
# Function to initialize the index
def initialize_index():
    global index
    # Specify the directory containing your text files
    directory_path = 'notepad_data'

    # Define the embedding model once
    Settings.embed_model = OpenAIEmbedding(embed_batch_size=10, model=OpenAIEmbeddingModelType.TEXT_EMBED_3_LARGE)
    Settings.llm = OpenAI()


    if not is_indexed(index_storage_dir):
        parent_nodes = parse_parent_nodes(directory_path)

        # Initialize list to hold all nodes (parents and leafs)
        all_nodes = []

        # For each parent node, create leaf nodes (sentences)
        for parent_node in parent_nodes:
            children = parse_child_nodes(parent_node)
            # Add the parent node to the list
            all_nodes += children
            all_nodes.append(parent_node)


        index.insert_nodes(all_nodes)
        index.storage_context.persist(persist_dir=index_storage_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=index_storage_dir)
        index = load_index_from_storage(storage_context)


def parse_child_nodes(parent_node):
    # Split parent node text into sentences
    children = parent_node.child_nodes or []
    sentences = nltk.sent_tokenize(parent_node.get_text())
    for sentence in sentences:
        # Create a leaf node for each sentence
        leaf_node = TextNode()
        leaf_node.set_content(sentence)
        leaf_node.relationships[NodeRelationship.PARENT] = parent_node.as_related_node_info()
        children.append(leaf_node.as_related_node_info())
    parent_node.relationships[NodeRelationship.CHILD] = children
    return children


def parse_parent_nodes(directory_path):
    # Read documents from the directory
    documents = SimpleDirectoryReader(directory_path).load_data()
    # Create parent nodes with larger chunk size
    parent_parser = SimpleNodeParser(chunk_size=256, chunk_overlap=50)
    parent_nodes = parent_parser.get_nodes_from_documents(documents)
    return parent_nodes


def is_indexed(index_storage_dir):
    return os.path.exists(index_storage_dir)


initialize_index()


def highlight_text_advanced(text, sentence=None):
    # If sentence is None, highlight the whole text
    if sentence is None:
        return f'<mark>{text}</mark>'
    else:
        # Split text into sentences
        sentences = nltk.sent_tokenize(text)
        highlighted_text = ''
        for s in sentences:
            # Compare sentences after stripping whitespace
            if s.strip() == sentence.strip():
                highlighted_text += f'<mark>{s}</mark> '
            else:
                highlighted_text += f'{s} '
        return highlighted_text.strip()


@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form['query']
        # Create query engine
        query_engine = index.as_query_engine(similarity_top_k=10)
        # Perform search
        response = query_engine.query(query)
        # Collect all similarity scores
        scores = [node_with_score.score for node_with_score in response.source_nodes]
        if scores:
            # Compute the 80th percentile threshold
            percentile_threshold = np.percentile(scores, 70)
            # Filter and process results
            for node_with_score in response.source_nodes:
                if node_with_score.score >= percentile_threshold:
                    node = node_with_score.node
                    # Check if node is a leaf node (has 'parent_node_id' in metadata)
                    if node.parent_node:
                        # Retrieve parent node's text
                        parent_node_id = node.parent_node.node_id
                        parent_node = index.docstore.get_node(parent_node_id)
                        parent_text = parent_node.get_text()
                        # Highlight relevant sentence in parent text
                        highlighted_text = highlight_text_advanced(parent_text, node.get_text())
                    else:
                        # Node is a parent node
                        print("Node is a parent !!!!")
                        parent_text = node.get_text()
                        highlighted_text = highlight_text_advanced(parent_text)
                    results.append({
                        'score': node_with_score.score,
                        'content': highlighted_text
                    })
            # Sort results by score in descending order
            results.sort(key=lambda x: x['score'], reverse=True)
        else:
            # Handle the case where no scores are available
            print("No results found.")
    return render_template('index.html', results=results, query=query)


# New route for chat functionality
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    messages = []
    if request.method == 'POST':
        user_input = request.form['user_input']
        # Process user input using the index
        # For simplicity, we'll generate a response using the index and a basic prompt
        query_engine = index.as_query_engine()
        response = query_engine.query(user_input)
        # Extract the response text
        if response.response:
            assistant_response = response.response.strip()
        else:
            assistant_response = "I'm sorry, I don't have an answer to that question."
        # Append messages
        messages.append({'sender': 'User', 'text': user_input})
        messages.append({'sender': 'Assistant', 'text': assistant_response})
        return render_template('chat.html', messages=messages)
    return render_template('chat.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=True, port=8888)

# app.py
