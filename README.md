[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/BesrourMS/yt2text)

# **YouTube Transcript to Article Generator**

This Python script automates the process of extracting subtitles from a YouTube video, structuring them into a dialogue format with speaker identification, and then generating a professional news article based on the transcript. It leverages the Groq API for advanced text processing and LangChain's RecursiveCharacterTextSplitter for efficient text chunking.

## **Features**

* **YouTube Subtitle Download:** Automatically fetches English subtitles (manual or auto-generated) from a given YouTube video URL.  
* **Speaker Separation:** Uses the Groq API to analyze transcripts, identify speakers (using names or contextual roles like "Researcher", "Interviewer"), and format the text into a clear dialogue.  
* **Article Generation:** Converts the processed transcript into a coherent, professional news article in AP style.  
* **Intelligent Text Chunking:** Employs LangChain's RecursiveCharacterTextSplitter to handle large transcripts by breaking them into manageable chunks for API processing, ensuring context is maintained.  
* **Output Formats:** Saves the generated article as a Markdown file (article.md) and a comprehensive JSON file (output.json) containing all intermediate and final data.  
* **Progress Tracking & Error Handling:** Provides console feedback during various stages of processing and includes robust error handling for API calls, subtitle downloads, and file operations.  
* **Rate Limit Management:** Includes random delays between Groq API calls to help mitigate potential rate limiting issues.  
* **Video Metadata Fetching:** Retrieves video title and thumbnail URL using YouTube's oEmbed API.

## **Installation**

1. **Clone the repository (or save the script):**
   ```bash
   git clone https://github.com/BesrourMS/yt2text/  
   cd yt2text
   ```
   (If you just have the script, save it as main.py for example)  
3. Install dependencies:  
   This script requires the following Python packages:  
   * requests  
   * youtube-transcript-api  
   * pytube  
   * langchain

You can install them using pip: 
```python 
pip install requests youtube-transcript-api pytube langchain
```

## **API Key Setup**

1. **Obtain a Groq API Key:**  
   * Go to the [Groq Console](https://console.groq.com/).  
   * Sign up or log in.  
   * Navigate to the "API Keys" section and generate a new API key.  
2. Configure the script:  
   Open the main.py file and replace "your\_api\_key" with your actual Groq API key:  
   ```python
   # Set your Groq API key
   GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
   ```
   **Important:** For production environments, consider using environment variables to store your API key instead of hardcoding it directly in the script for security reasons.

## **Usage**

1. **Run the script:**  
```python
   python main.py
```
3. Enter YouTube URL:  
   The script will prompt you to enter the YouTube video URL:  
   Enter the YouTube video URL:

   Paste the full URL of the YouTube video you want to process (e.g., [https://www.youtube.com/watch?v=dQw4w9WgXcQ](https://www.youtube.com/watch?v=OpBGgntJqtM)).  
4. Monitor progress:  
   The script will display messages in the console indicating its progress:  
   * Downloading subtitles  
   * Processing subtitles (chunk by chunk)  
   * Generating article (chunk by chunk)  
   * Saving files

## **Output Files**

Upon successful execution, the script will create the following files in the same directory:

* transcript\_raw.srt: The raw, downloaded SRT formatted transcript of the video.  
* article.md: The generated news article in Markdown format.  
* output.json: A JSON file containing all the raw subtitles, structured transcript, the final article, and video metadata (title, thumbnail, URL).

## **Error Handling**

The script includes error handling for common issues such as:

* Invalid YouTube URL.  
* Failure to download subtitles (e.g., no English transcripts available).  
* Groq API call failures (network issues, invalid API key, rate limits).  
* File saving errors.

If an error occurs, an error message will be printed to the console.

## **Customization**

* **Chunking Parameters:** You can adjust chunk\_size and chunk\_overlap in chunk\_text\_with\_langchain for both subtitle processing and article generation to fine-tune how the text is divided.  
  * process\_subtitles: uses smaller chunks and overlap for detailed speaker identification.  
  * generate\_article: uses larger chunks and overlap for better contextual understanding during article generation.  
* **Groq Model:** The script currently uses "llama-3.3-70b-versatile". You can change this to another available Groq model if desired.  
* **Temperature:** The temperature parameter in groq\_api\_call (set to 0.7) controls the creativity of the AI. Lower values make the output more deterministic, while higher values lead to more varied and creative responses.  
* **Wait Times:** The random wait times between API calls (random.uniform(5, 10)) can be adjusted if you encounter persistent rate limiting issues or wish to speed up/slow down the process.
