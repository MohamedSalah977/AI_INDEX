import os
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import cv2
import vlc
import whisper
from ultralytics import YOLO

VIDEO_FOLDER = r"C:\Users\salah\OneDrive\Desktop\indexation\videos"

class VideoIndexer:
    def __init__(self):
        self.model_yolo = YOLO("yolov8n.pt")
        self.model_whisper = whisper.load_model("base")
        self.index = {}
#Initializes YOLO and Whisper models and prepares a dictionary (index) to store video data.
    def index_videos(self, progress_callback=None):
        videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(('.mp4', '.avi', '.mov'))]
        total = len(videos)
        for i, video in enumerate(videos):
            video_path = os.path.join(VIDEO_FOLDER, video)
            objects = self.detect_objects(video_path)
            transcript = self.transcribe_audio(video_path)
            self.index[video_path] = {"objects": objects, "transcript": transcript}
            if progress_callback:
                progress_callback((i + 1) / total)
#Loops through videos, runs object detection & transcription, saves results in index, and updates the progress bar.
    def detect_objects(self, video_path):
        try:
            # Réduction du nombre de frames analysées
            result = self.model_yolo.predict(video_path, stream=True, vid_stride=5)
            detected = set()
            for frame in result:
                for box in frame.boxes:
                    cls_id = int(box.cls[0])
                    label = self.model_yolo.names[cls_id]
                    detected.add(label)
            return list(detected)
        except Exception as e:
            print(f"Erreur détection objets : {e}")
            return []
#Analyzes every 15th frame to detect objects using YOLO and returns a list of unique labels.
    def transcribe_audio(self, video_path):
        try:
            result = self.model_whisper.transcribe(video_path)
            return result["text"].lower()
        except Exception as e:
            print(f"Erreur transcription : {e}")
            return ""

class VideoSearcher:
    def __init__(self):
        self.index = {}

    def update_index(self, index):
        self.index = index

    def search(self, query):
        results = []
        for path, data in self.index.items():
            if query.lower() in data["transcript"] or any(query.lower() in obj.lower() for obj in data["objects"]):
                results.append((os.path.basename(path), path))
        return results

class VideoApp:
    import os
    import tkinter as tk
    from tkinter import ttk, messagebox
    from threading import Thread
    import vlc
    import whisper
    import cv2
    from ultralytics import YOLO

    VIDEO_FOLDER = r"C:\Users\salah\OneDrive\Desktop\indexation\videos"

    class VideoIndexer:
        def __init__(self):
            self.model_yolo = YOLO("yolov8n.pt")
            self.model_whisper = whisper.load_model("base")
            self.index = {}

        def index_videos(self, progress_callback=None):
            videos = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(('.mp4', '.avi', '.mov'))]
            total = len(videos)
            for i, video in enumerate(videos):
                video_path = os.path.join(VIDEO_FOLDER, video)
                print(f"\nIndexation de : {video_path}")
                objects = self.detect_objects(video_path)
                transcript = self.transcribe_audio(video_path)
                print(f"Objets détectés : {objects}")
                print(f"Transcript : {transcript}")
                self.index[video_path] = {"objects": objects, "transcript": transcript}
                if progress_callback:
                    progress_callback((i + 1) / total)

        def detect_objects(self, video_path):
            try:
                cap = cv2.VideoCapture(video_path)
                frame_count = 0
                detected = set()
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1
                    if frame_count % 15 != 0:  # Réduit les frames analysées
                        continue
                    results = self.model_yolo.predict(source=frame, conf=0.4, verbose=False)
                    for r in results:
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            label = self.model_yolo.names[cls_id]
                            detected.add(label)
                cap.release()
                return list(detected)
            except Exception as e:
                print(f"Erreur détection objets : {e}")
                return []
#Analyzes every 15th frame to detect objects using YOLO and returns a list of unique labels.


        def transcribe_audio(self, video_path):
            try:
                result = self.model_whisper.transcribe(video_path, language="en")
                print("Transcription Whisper :", result["text"])
                return result["text"].lower()
            except Exception as e:
                print(f"Erreur transcription : {e}")
                return ""
#Transcribes the video’s audio with Whisper and returns lowercase text.
    class VideoSearcher:
        def __init__(self):
            self.index = {}

        def update_index(self, index):
            self.index = index

        def search(self, query):
            results = []
            for path, data in self.index.items():
                if query.lower() in data["transcript"] or any(query.lower() in obj.lower() for obj in data["objects"]):
                    results.append((os.path.basename(path), path))
            return results
#Updates and searches the video index. Returns a list of matching video names and paths.
    class VideoApp:
        def __init__(self, root):
            self.root = root
            self.root.title("Recherche Vidéo Intelligente")
            self.root.geometry("700x500")
            self.root.configure(bg="#f0f0f0")
#Initializes the main app window with title, size, and background.


            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TLabel", font=("Helvetica", 12))
            style.configure("TButton", font=("Helvetica", 11), padding=6)
            style.configure("TEntry", font=("Helvetica", 11))
            style.configure("TProgressbar", thickness=20)

            self.indexer = VideoIndexer()
            self.searcher = VideoSearcher()

            self.setup_ui()
            self.start_indexing()
#Creates instances of indexer & searcher, sets up the UI, and starts background indexing.
        def setup_ui(self):
            main_frame = tk.Frame(self.root, padx=30, pady=30, bg="#f0f0f0")
            main_frame.pack(fill=tk.BOTH, expand=True)

            search_frame = tk.Frame(main_frame, bg="#f0f0f0")
            search_frame.pack(fill=tk.X, pady=15)

            tk.Label(search_frame, text="Sujet :", bg="#f0f0f0", font=("Helvetica", 12)).pack(side=tk.LEFT)
            self.search_entry = ttk.Entry(search_frame, width=40)
            self.search_entry.pack(side=tk.LEFT, padx=10)
            self.search_entry.bind("<Return>", lambda e: self.search_videos())

            search_btn = ttk.Button(search_frame, text="Rechercher", command=self.search_videos)
            search_btn.pack(side=tk.LEFT)

            self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
            self.progress.pack(pady=15)

            self.results_list = tk.Listbox(main_frame, height=12, font=("Helvetica", 11), bg="white", fg="black")
            self.results_list.pack(fill=tk.BOTH, expand=True, pady=5)
            self.results_list.bind("<Double-Button-1>", lambda e: self.play_video())

            self.status = tk.StringVar()
            self.status.set("Indexation en cours...")
            tk.Label(main_frame, textvariable=self.status, bg="#f0f0f0", font=("Helvetica", 11, "italic")).pack(pady=10)

        def start_indexing(self):
            Thread(target=self.run_indexing, daemon=True).start()

        def run_indexing(self):
            try:
                self.indexer.index_videos(progress_callback=self.update_progress)
                self.searcher.update_index(self.indexer.index)
                self.status.set("Indexation terminée !")
                messagebox.showinfo("Succès", "Indexation terminée avec succès")
            except Exception as e:
                self.status.set(f"Erreur: {str(e)}")
                messagebox.showerror("Erreur", f"Échec de l'indexation: {e}")
#Runs video indexing in the background and updates the UI when finished.
        def update_progress(self, value):
            self.progress["value"] = value * 100
            self.root.update_idletasks()

        def search_videos(self):
            query = self.search_entry.get()
            if not query:
                messagebox.showwarning("Erreur", "Veuillez entrer un sujet")
                return

            self.status.set(f"Recherche: {query}...")
            self.results_list.delete(0, tk.END)

            results = self.searcher.search(query)
            if not results:
                self.results_list.insert(tk.END, "Aucun résultat trouvé")
                self.status.set("Aucun résultat")
                return

            for video, path in results:
                self.results_list.insert(tk.END, path)

            self.status.set(f"{len(results)} résultats trouvés")
#Gets the query, searches for matches, and displays the results in the listbox.
        def play_video(self):
            selection = self.results_list.curselection()
            if not selection:
                messagebox.showwarning("Erreur", "Veuillez sélectionner une vidéo")
                return

            video_path = self.results_list.get(selection[0])
            player = vlc.MediaPlayer(video_path)
            player.play()

    if __name__ == "__main__":
        root = tk.Tk()
        app = VideoApp(root)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
