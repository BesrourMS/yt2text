# YouTube Transcript to Article Converter

A Python tool that converts YouTube video transcripts into professionally formatted articles using the Groq AI API. This application downloads video subtitles, processes speaker dialogues, and generates well-structured news articles.

## Features

- Downloads YouTube video subtitles (both manual and auto-generated)
- Supports multiple languages with automatic translation to English
- Processes transcripts to identify and separate speakers
- Generates professional news articles following AP style guidelines
- Exports results in both Markdown and JSON formats
- Implements smart chunking for handling long transcripts
- Includes rate limiting and error handling

## Prerequisites

- Python 3.6+
- Groq API key
- Required Python packages:
  - pytube
  - youtube-transcript-api
  - requests
  - typing
  - datetime

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-transcript-processor.git
cd youtube-transcript-processor
```

2. Install required packages:
```bash
pip install pytube youtube-transcript-api requests
```

3. Set up your Groq API key:
   - Create a Groq account and obtain your API key
   - Replace `your_api_key` in the code with your actual API key

## Usage

1. Run the script:
```bash
python main.py
```

2. Enter a YouTube URL when prompted
3. The script will:
   - Download the video transcript
   - Process the dialogue
   - Generate an article
   - Save outputs as both Markdown and JSON files

## Output Files

The script generates three main output files:
- `transcript_raw.srt`: Raw subtitle file in SRT format
- `article.md`: Generated article in Markdown format
- `output.json`: Complete data including raw subtitles, structured transcript, and article

## Examples  

Here’s an example of a video processed by the tool:  

- **YouTube Video**: [How firefighting planes and helicopters are battling the LA fires](https://www.youtube.com/watch?v=0d-uc8p5GrE)  
- **Generated Article**: [arida.tn/how-firefighting-planes-and-helicopters-are-battling-the-la-fires](https://arida.tn/how-firefighting-planes-and-helicopters-are-battling-the-la-fires)  

## Functions

### Core Functions

- `download_subtitles(video_url)`: Downloads and extracts YouTube subtitles
- `process_subtitles(subtitles)`: Processes subtitles to identify speakers and format dialogue
- `generate_article(transcript)`: Converts processed transcript into a news article
- `chunk_text(text, chunk_size)`: Splits large texts into manageable chunks

### Helper Functions

- `groq_api_call(prompt, task)`: Makes API calls to Groq
- `get_video_id(url)`: Extracts video ID from YouTube URLs
- `format_time(seconds)`: Converts seconds to SRT timestamp format
- `save_as_markdown(article)`: Saves the article in Markdown format
- `save_as_json(data)`: Saves all data in JSON format

## Error Handling

The script includes comprehensive error handling for:
- Invalid YouTube URLs
- Failed subtitle downloads
- API call failures
- File saving errors
- Rate limiting issues

## Rate Limiting

The script implements random delays between API calls:
- 5-10 seconds between transcript processing chunks
- 3-5 seconds between article generation segments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Uses the Groq API for AI text processing
- Built with pytube for YouTube video processing
- Utilizes youtube-transcript-api for subtitle extraction

## Disclaimer

This tool is dependent on YouTube's subtitle availability and quality. Results may vary based on the source video's transcript quality and availability.
