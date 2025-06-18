import json
import requests
from typing import Dict, Any, List
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract
import time
import random
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set your Groq API key
GROQ_API_KEY = "your_api_key"

def chunk_text_with_langchain(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Chunks text using LangChain's RecursiveCharacterTextSplitter.

    Args:
        text: The text to be chunked.
        chunk_size: The maximum size of each chunk (in characters).
        chunk_overlap: The number of characters to overlap between chunks.

    Returns:
        A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        # The most important parameter: the maximum size of each chunk.
        chunk_size=chunk_size,
        
        # A vital parameter for maintaining context between chunks.
        # It creates a "sliding window" effect.
        chunk_overlap=chunk_overlap,
        
        # Measures the length of chunks by number of characters.
        length_function=len,
        
        # This is the "magic" of the splitter. It will try to split on these
        # separators in order. The default is ["\n\n", "\n", " ", ""].
        # For SRT files, this default is excellent.
        is_separator_regex=False,
    )
    
    return text_splitter.split_text(text)

def groq_api_call(prompt: str, task: str) -> str:
    """
    Make a call to the Groq API with error handling and proper endpoint
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"API call failed: {str(e)}")

def get_video_id(url: str) -> str:
    """
    Extract video ID from YouTube URL using pytube's extract.video_id
    """
    try:
        video_id = extract.video_id(url)
        return video_id
    except Exception:
        raise ValueError("Could not extract video ID from URL")

def download_subtitles(video_url: str) -> str:
    """
    Download and extract English subtitles or auto-generated captions from a YouTube video,
    preferring 'en-US' and 'en-GB' over general 'en' if available.
    """
    try:
        video_id = get_video_id(video_url)
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("✅ Available transcripts:", [t.language_code for t in transcript_list])
        preferred_langs = ['en-US', 'en-GB', 'en']
        
        try:
            # Try to find a manually created transcript in preferred languages
            transcript = transcript_list.find_manually_created_transcript(preferred_langs)
            print("🎯 Using manually created transcript.")
        except:
            try:
                # If not found, try a generated transcript in preferred languages
                transcript = transcript_list.find_generated_transcript(preferred_langs)
                print("🎯 Using auto-generated transcript.")
            except:
                # If still not found, find any translatable transcript and translate to 'en'
                for t in transcript_list:
                    if t.is_translatable:
                        transcript = t.translate('en')
                        break
                else:
                    raise ValueError("No translatable transcript found")
        
        # Fetch the transcript data
        transcript_data = transcript.fetch()
        
        # Format the transcript into SRT format
        srt_content = ""
        for i, entry in enumerate(transcript_data.to_raw_data(), 1):
            start_time = format_time(entry['start'])
            end_time = format_time(entry['start'] + entry['duration'])
            text = entry['text']
            srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
        
        # Save to file and return the content
        with open("transcript_raw.srt", "w", encoding="utf-8") as file:
            file.write(srt_content)
            
        return srt_content
            
    except Exception as e:
        raise Exception(f"Failed to download subtitles: {str(e)}")

def format_time(seconds: float) -> str:
    """
    Convert seconds to SRT time format (HH:MM:SS,mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def process_subtitles(subtitles: str) -> str:
    """
    Process subtitles using Groq API to separate speakers, handling large transcripts in chunks.
    """
    # Using the new LangChain chunker
    # A smaller chunk size is good for the detailed task of speaker identification.
    # A small overlap helps maintain context of who was last speaking.
    chunks = chunk_text_with_langchain(subtitles, chunk_size=3500, chunk_overlap=150)
    processed_chunks = []

    print(f"Processing transcript in {len(chunks)} chunks using LangChain splitter...")

    for i, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {i}/{len(chunks)}...")
        prompt = f"""
        Analyze this part of a subtitle file from a video and format it as a clear dialogue.
        Please separate the text by speaker and remove timestamp information.
        If you recognize any speaker names, use them. If names aren't available, identify speakers using natural, contextually appropriate role descriptions (e.g., "Researcher," "Interviewer," "Physician") based on their expertise, perspective, or function in the conversation. Format these roles as direct speaker labels rather than inserting phrases like "as an expert noted." Avoid generic labels like "Speaker 1" or "Speaker 2."

        
        Subtitle chunk:
        {chunk}
        """
        processed_chunk = groq_api_call(prompt, task="dialogue_formatting")

        # Add a random wait time between 5 and 10 seconds
        wait_time = random.uniform(5, 10)
        print(f"Waiting for {wait_time:.2f} seconds before the next API call...")
        time.sleep(wait_time)

        processed_chunks.append(processed_chunk)

    return "\n\n".join(processed_chunks)

def generate_article(transcript: str) -> str:
    """
    Generate an article from the processed transcript, handling large transcripts in chunks.
    """
    # Using the LangChain chunker again, but with parameters tuned for article writing.
    # A larger chunk size gives the model more context for summarization.
    # A larger overlap ensures the narrative flows smoothly across chunks.
    chunks = chunk_text_with_langchain(transcript, chunk_size=10000, chunk_overlap=500)
    article_chunks = []

    print(f"Generating article in {len(chunks)} parts using LangChain splitter...")
    
    # This logic can be simplified now, as we don't need special prompts for the first/last chunk
    # thanks to the robustness of the chunking strategy.
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Generating article part {i}/{len(chunks)}...")
        
        # Determine the right prompt based on the chunk's position
        if i == 1 and len(chunks) > 1:
            prompt_template = "This is the first part of a transcript. Start writing a professional news article in AP style based on it. Include a strong introduction."
        elif i == len(chunks) and len(chunks) > 1:
            prompt_template = "This is the final part of a transcript. Continue the article based on it, providing a strong concluding paragraph."
        elif len(chunks) == 1:
            prompt_template = "Convert this transcript into a complete, professional news article in AP style, including an introduction and conclusion."
        else: # Middle chunks
            prompt_template = "This is a middle part of a transcript. Continue the news article in a consistent journalistic style based on this content."

        prompt = f"""
        {prompt_template}
        
        Transcript Part:
        {chunk}
        """
        
        article_part = groq_api_call(prompt, task="article_writing")
        article_chunks.append(article_part)

        # Add a random wait time
        if i < len(chunks):
            wait_time = random.uniform(5, 10)
            print(f"Waiting for {wait_time:.2f} seconds before the next API call...")
            time.sleep(wait_time)

    return "\n\n".join(article_chunks)

def save_as_markdown(article: str, file_name: str = "article.md") -> None:
    """
    Save the generated article as a Markdown file
    """
    try:
        with open(file_name, "w", encoding="utf-8") as md_file:
            md_file.write(article)
        print(f"Article saved successfully as {file_name}")
    except IOError as e:
        raise Exception(f"Failed to save markdown file: {str(e)}")

def save_as_json(data: Dict[str, Any], file_name: str = "output.json") -> None:
    """
    Save the structured data as a JSON file
    """
    try:
        with open(file_name, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Data saved successfully as {file_name}")
    except IOError as e:
        raise Exception(f"Failed to save JSON file: {str(e)}")

def fetch_oembed_data(video_url: str) -> Dict[str, Any]:
    """
    Fetch oEmbed data from YouTube API
    """
    oembed_url = f"https://www.youtube.com/oembed?url={video_url}&format=json"
    try:
        response = requests.get(oembed_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch oEmbed data: {str(e)}")

def main():
    """
    Main execution function with progress tracking and error handling
    """
    try:
        video_url = input("Enter the YouTube video URL: ").strip()
        
        if not video_url:
            raise ValueError("Please provide a valid YouTube URL")
        
        print("\nStarting transcript processing pipeline...")
        
        # Fetch oEmbed data
        print("📥 Fetching oEmbed data...")
        oembed_data = fetch_oembed_data(video_url)
        video_title = oembed_data.get("title", "Unknown Title")
        video_thumbnail = oembed_data.get("thumbnail_url", "")

        # Step 1: Download Subtitles
        print("📥 Downloading subtitles...")
        subtitles = download_subtitles(video_url)
        
        # Step 2: Process Subtitles
        print("🔄 Processing subtitles...")
        structured_transcript = process_subtitles(subtitles)
        
        # Add a random wait time between 5 and 10 seconds
        wait_time = random.uniform(5, 10)
        print(f"Waiting for {wait_time:.2f} seconds before Generating article...")
        time.sleep(wait_time)
        
        # Step 3: Generate Article
        print("✍️ Generating article...")
        article = generate_article(structured_transcript)
        
        # Step 4: Save Article as Markdown
        print("💾 Saving article...")
        save_as_markdown(article)
        
        # Step 5: Save Structured Data as JSON
        print("📊 Saving structured data...")
        output_data = {
            "video_url": video_url,
            "title": video_title,
            "thumbnail": video_thumbnail,
            "raw_subtitles": subtitles,
            "structured_transcript": structured_transcript,
            "article": article,
            "metadata": {
                "processing_timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        save_as_json(output_data)
        
        print("\n✅ Process completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
