from googleapiclient.discovery import build
from utils import DownloadPathManager, format_duration, is_valid_url, open_directory, DEFAULT_PATH
import os
import yt_dlp
import webbrowser
import isodate

API = "QlJVSCBVU0UgWU9VUiBPV04gQVBJIEtFWQ==" # adjust your API
 
def youtube_music():
    query = input("Search Music Title: ")
    videos = youtube_query(query)

    if not videos:
        print("No Results Found.")
        return

    print("\n===== Music Genre Search Results =====")
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['Title']}")
        print(f"   Channel: {video['Channel']}")
        print(f"   Video ID: {video['Video ID']}")
        print(f"   Duration: {video['Duration']}")
        print(f"   Published: {video['Published']}")

    while True:
        option = input("\nSelect Video to Preview/Download (0 to Menu): ")
        if option == '0':
            break

        if option.isdigit() and 1 <= int(option) <= len(videos):
            selected_video = videos[int(option) - 1]
            print(f"\n > Selected: {selected_video['Title']}")
        else:
            print("\n > ! Invalid Option")
            continue

        preview = input("\nPreview Music Video? (y/n): ").lower()
        if preview == 'y':
            webbrowser.open(f"https://youtube.com/watch?v={selected_video['Video ID']}")

        download = input("\nConvert to MP3? (y/n): ").lower()
        if download == 'y':
            try:
                download_path = organize_path()

                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                    'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    print(f"\n > Downloading: {selected_video['Title']}\n")
                    ydl.download([f"https://youtube.com/watch?v={selected_video['Video ID']}"])

                print("\n > Download Completed!")
                break

            except Exception as e:
                print(f"\n > Error Occurred: {e}")
        else:
            break
         

def youtube_link():
    link = input("Enter the URL: ").strip()
    
    if not is_valid_url(link):
        print("\n > ! Invalid URL")
        return
    
    download_path = organize_path()
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"\n > Downloading...")
        ydl.download(link)

    print("\n > Download Completed!")


def youtube_query(query):
    try:
        youtube = build("youtube", "v3", developerKey=API)
        request = youtube.search().list(
            q=query + "music", part="snippet", type="video", maxResults=15
        )
        
        response = request.execute()

        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        
        videos_request = youtube.videos().list(
            part="contentDetails", 
            id=",".join(video_ids)
        )
        videos_response = videos_request.execute()
        
        duration_dict = {
            video['id']: int(isodate.parse_duration(video['contentDetails']['duration']).total_seconds())
            for video in videos_response.get('items', [])
        }

        videos = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            
            try:
                duration = duration_dict.get(video_id, "Unknown")
                duration_formatted = format_duration(duration)
                
                videos_info = {
                    "Title": item["snippet"]["title"],
                    "Channel": item["snippet"]["channelTitle"],
                    "Video ID": video_id,
                    "Duration": duration_formatted,
                    "Published": item["snippet"]["publishedAt"][:10]
                }
                videos.append(videos_info)
                
            except Exception as e:
                print(f"\n > ! Error Occurred. ID: {video_id}, Error: {e}")
        
        return videos
    
    except Exception as e:
        print(f"Error: {e}")
        return []


def organize_path():
    manager = DownloadPathManager()
    current_path = DEFAULT_PATH

    while True:
        print("\n===== Available Location =====")
        print("\n0. Add New Path")
        for i, path in enumerate(manager.paths.values(), start=1):
            print(f"{i}. {path}")

        option = input("\nSelect Download Location (Press Enter for Default): ")

        if option == "":  
            print(f"\n > Using Default Path: {current_path}")
            return current_path

        if option.isdigit(): 
            option = int(option)
            if option == 0:  
                manager.add_paths()
                continue 
            elif 1 <= option <= len(manager.paths):  
                selected_path = list(manager.paths.values())[option - 1]
                print(f"\n > Selected Path: {selected_path}")
                return selected_path
            else:  
                print("\n > ! Invalid Option. Try Again.")
        else:  
            print("\n > ! Invalid Input. Try Again.")


def open_playlist():
    manager = DownloadPathManager()

    while True:
        print("\n===== Available Locations =====")
        print("\n0. Exit")
        for i, path in enumerate(manager.paths.values(), start=1):
            print(f"{i}. {path}")

        option = input("\nChoose Location (0 to Menu): ").strip()

        if option == "0":
            break

        if option.isdigit() and 1 <= int(option) <= len(manager.paths):
            selected_path = list(manager.paths.values())[int(option) - 1]

            print(f"\n > Opening Location: {selected_path}")
            try:
                open_directory(selected_path)
            except Exception as e:
                print(f"\n > ! Error Opening Directory: {e}")
        else:
            print("\n > ! Invalid Option.")





            
        
