import json
from pytube import YouTube
import requests
from typing import Dict, Any, List
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# Set your Groq API key
GROQ_API_KEY = "your_api_key"

def chunk_text(text: str, chunk_size: int = 12000) -> List[str]:
    """
    Split text into chunks based on SRT entries
    """
    chunks = []
    current_chunk = []
    current_size = 0
    
    # Split into individual SRT entries
    entries = text.strip().split('\n\n')
    
    for entry in entries:
        entry_size = len(entry)
        if current_size + entry_size > chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []
            current_size = 0
        
        current_chunk.append(entry)
        current_size += entry_size
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

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
    Extract video ID from YouTube URL
    """
    try:
        if "youtu.be" in url:
            return url.split("/")[-1]
        elif "youtube.com" in url:
            return url.split("v=")[1].split("&")[0]
        else:
            raise ValueError("Invalid YouTube URL format")
    except Exception:
        raise ValueError("Could not extract video ID from URL")

def download_subtitles(video_url: str) -> str:
    """
    Download and extract English subtitles or auto-generated captions from a YouTube video
    """
    try:
        video_id = get_video_id(video_url)
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except:
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    transcript = transcript_list.find_transcript(['en'])
                    if not transcript.is_translatable:
                        raise ValueError("No translatable transcript found")
                    transcript = transcript.translate('en')
            
            transcript_data = transcript.fetch()
            
            srt_content = ""
            for i, entry in enumerate(transcript_data, 1):
                start_time = format_time(entry['start'])
                end_time = format_time(entry['start'] + entry['duration'])
                text = entry['text']
                srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
            
            with open("transcript_raw.srt", "w", encoding="utf-8") as file:
                file.write(srt_content)
                
            return srt_content
            
        except Exception as e:
            raise Exception(f"Failed to get transcript: {str(e)}")
            
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
    Process subtitles using Groq API to separate speakers, handling large transcripts in chunks
    """
    chunks = chunk_text(subtitles)
    processed_chunks = []
    
    print(f"Processing transcript in {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"Processing chunk {i}/{len(chunks)}...")
        prompt = f"""
        Analyze this part of a subtitle file from a video and format it as a clear dialogue.
        Please separate the text by speaker and remove timestamp information.
        If you recognize any speaker names, use them, otherwise distinguish between speakers by their speech patterns or content context without adding placeholder labels..
        
        Subtitle chunk:
        {chunk}
        """
        processed_chunk = groq_api_call(prompt, task="dialogue_formatting")
        processed_chunks.append(processed_chunk)
    
    return "\n\n".join(processed_chunks)

def generate_article(transcript: str) -> str:
    """
    Generate an article from the processed transcript, handling large transcripts in chunks
    """
    chunks = chunk_text(transcript, chunk_size=10000)
    article_chunks = []
    
    print(f"Generating article in {len(chunks)} parts...")
    
    # Process first chunk with introduction
    first_chunk = chunks[0]
    prompt = f"""
    Convert this first part of an interview transcript into the beginning of a professional news article.
    Include a strong introduction and follow AP style guidelines.
    
    Transcript part:
    {first_chunk}
    """
    article_chunks.append(groq_api_call(prompt, task="article_writing"))
    
    # Process middle chunks
    for i, chunk in enumerate(chunks[1:-1], 2):
        print(f"Processing part {i}/{len(chunks)}...")
        prompt = f"""
        Continue the article with this part of the transcript.
        Maintain the flow and journalistic style.
        
        Transcript part:
        {chunk}
        """
        article_chunks.append(groq_api_call(prompt, task="article_writing"))
    
    # Process final chunk with conclusion
    if len(chunks) > 1:
        final_chunk = chunks[-1]
        prompt = f"""
        Conclude the article with this final part of the transcript.
        Provide a strong closing and maintain journalistic style.
        
        Transcript part:
        {final_chunk}
        """
        article_chunks.append(groq_api_call(prompt, task="article_writing"))
    
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

def main():
    """
    Main execution function with progress tracking and error handling
    """
    try:
        video_url = input("Enter the YouTube video URL: ").strip()
        
        if not video_url:
            raise ValueError("Please provide a valid YouTube URL")
        
        print("\nStarting transcript processing pipeline...")
        
        # Step 1: Download Subtitles
        print("📥 Downloading subtitles...")
        subtitles = download_subtitles(video_url)
        
        # Step 2: Process Subtitles
        print("🔄 Processing subtitles...")
        structured_transcript = process_subtitles(subtitles)
        
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
