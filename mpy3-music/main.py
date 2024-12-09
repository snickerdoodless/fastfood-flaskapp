from mpy3 import youtube_music, youtube_link, open_playlist

def menu():
    print("""\n
        ███╗   ███╗██████╗ ██╗   ██╗██████╗       ███╗   ███╗██╗   ██╗███████╗██╗ ██████╗
        ████╗ ████║██╔══██╗╚██╗ ██╔╝╚════██╗      ████╗ ████║██║   ██║██╔════╝██║██╔════╝
        ██╔████╔██║██████╔╝ ╚████╔╝  █████╔╝█████╗██╔████╔██║██║   ██║███████╗██║██║     
        ██║╚██╔╝██║██╔═══╝   ╚██╔╝   ╚═══██╗╚════╝██║╚██╔╝██║██║   ██║╚════██║██║██║     
        ██║ ╚═╝ ██║██║        ██║   ██████╔╝      ██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗
        ╚═╝     ╚═╝╚═╝        ╚═╝   ╚═════╝       ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝                                                                                                                                                              
        """)
    while True:
        print("\n=== ♪♫♪  Mpy3 Music Downloader Menu ♪♫♪ === ")
        print("\n1. Search Videos to Download")
        print("2. Copy-Paste YouTube Link")                 
        print("3. Open Path Playlist")
        print("4. Exit Program")
        print("\n============================================")
        
        choice = input("Select an option (1-5): ")
        
        if choice == '1':
            youtube_music()
        elif choice == '2':
            youtube_link()
        elif choice == '3':
            open_playlist()
        elif choice == '4':
            print("\n > Exiting program. Goodbye!")
            break
        else:
            print("\n> ! Invalid option. Please try again.")

if __name__=="__main__":
    menu()