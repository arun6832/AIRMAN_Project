### How to Use

To use the AIRMAN application, ensure you have Python 3.10 or above installed on your system. Create and activate a virtual environment inside the project folder, then install all the required packages using the provided `requirements.txt` file. This prepares your system with Streamlit, PDF processing libraries, and the AI modules required for the app to function.

Next, place your aircraft POH (Pilot Operating Handbook) PDF files inside a folder named `data` located in the project root directory. The AIRMAN system automatically scans and reads these manuals to extract aircraft limitations through its RAG-based (Retrieval-Augmented Generation) engine. Make sure your POH files are stored in `C:\Airman\data\` or the equivalent directory on your system.

Finally, start the application using the command `streamlit run app/streamlit_app.py`. This launches the AIRMAN dashboard in your browser, where you can enter departure and destination airports, choose your aircraft type, select runway information, and generate a complete AI-assisted preflight report. The system automatically retrieves weather data, interprets POH limits, calculates runway suitability, and creates a downloadable safety PDF.
